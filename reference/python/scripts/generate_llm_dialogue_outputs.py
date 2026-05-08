#!/usr/bin/env python3
"""Generate CAP LLM dialogue benchmark outputs through an OpenAI-compatible API.

This script is the live LLM-in-the-loop side of the benchmark. Use
`--dry-run` to build the prompt manifest without calling an LLM.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cap.proxy_policy import build_policy, parse_compact_telemetry


ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = ROOT / "validation_artifacts" / "llm_dialogue_benchmark"
DEFAULT_CASE_DIR = BENCH_ROOT / "cases"
DEFAULT_TEMPLATE_DIR = BENCH_ROOT / "prompt_templates"
DEFAULT_OUTPUT = BENCH_ROOT / "model_outputs" / "live_outputs.json"
DEFAULT_MODELS = ["comet_12b_v.7-i1", "silicon-maid-7b-imatrix"]
DEFAULT_MODES = [
    "prompt_only",
    "rag_only",
    "validator_only",
    "prompt_level_cap",
    "proxy_level_cap",
]


def load_cases(case_dir: Path, limit: int | None = None) -> list[dict]:
    cases = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(case_dir.glob("*.json"))
    ]
    return cases[:limit] if limit else cases


def filter_cases(cases: list[dict], case_ids: list[str]) -> list[dict]:
    if not case_ids:
        return cases
    wanted = set(case_ids)
    selected = [case for case in cases if case.get("case_id") in wanted]
    missing = sorted(wanted.difference(str(case.get("case_id")) for case in selected))
    if missing:
        raise SystemExit(f"Requested case ids not found: {', '.join(missing)}")
    return selected


def load_template(template_dir: Path, mode: str) -> str:
    return (template_dir / f"{mode}.md").read_text(encoding="utf-8")


def render_prompt(case: dict, mode: str, template_dir: Path) -> str:
    template = load_template(template_dir, mode)
    replacements = {
        "case_title": case["title"],
        "dialogue_context": render_dialogue(case.get("dialogue_context", [])),
        "evidence": render_list(case.get("evidence", [])),
        "telemetry_tag": case.get("telemetry_tag", ""),
        "cap_policy": render_cap_policy(case),
    }
    prompt = template
    for key, value in replacements.items():
        prompt = prompt.replace("{{" + key + "}}", value)
    return prompt


def render_dialogue(messages: list[dict]) -> str:
    return "\n".join(f"{item['role']}: {item['content']}" for item in messages)


def render_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_cap_policy(case: dict) -> str:
    flags = case.get("cap_flags", {})
    telemetry = parse_compact_telemetry(case["telemetry_tag"])
    policy = build_policy(
        telemetry,
        user_counter_source=bool(flags.get("user_counter_source", False)),
        source_validity=str(flags.get("source_validity", "unknown")),
        false_user_frame=bool(flags.get("false_user_frame", False)),
        stale_anchor=bool(flags.get("stale_anchor", False)),
    )
    return "\n".join(
        [
            f"node_status = {policy.node_status}",
            f"allowed_as_anchor = {policy.allowed_as_anchor}",
            f"release_action = {policy.release_action}",
            f"forbid = {', '.join(policy.forbid) or 'none'}",
            f"require = {', '.join(policy.require) or 'none'}",
            f"reasons = {', '.join(policy.reasons) or 'none'}",
        ]
    )


def request_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    api_key: str | None = None,
    timeout: float = 120.0,
) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc.reason}") from exc


def get_available_models(base_url: str, api_key: str | None, timeout: float) -> list[str]:
    payload = request_json(f"{base_url.rstrip('/')}/models", api_key=api_key, timeout=timeout)
    return [item.get("id", "") for item in payload.get("data", []) if item.get("id")]


def call_chat_completion(
    base_url: str,
    *,
    model: str,
    prompt: str,
    api_key: str | None,
    timeout: float,
    temperature: float,
    max_tokens: int,
    retries: int = 0,
    retry_delay_seconds: float = 30.0,
) -> dict:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are participating in a benchmark. Answer the task directly. "
                    "Do not mention that you are being benchmarked unless required by the prompt."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    for attempt in range(retries + 1):
        try:
            return request_json(
                f"{base_url.rstrip('/')}/chat/completions",
                method="POST",
                payload=payload,
                api_key=api_key,
                timeout=timeout,
            )
        except RuntimeError as exc:
            if attempt >= retries or not is_retryable_api_error(str(exc)):
                raise
            print(
                f"{model} | retry {attempt + 1}/{retries} after transient API error: {exc}",
                file=sys.stderr,
            )
            time.sleep(retry_delay_seconds)
    raise RuntimeError("unreachable retry loop state")


def is_retryable_api_error(message: str) -> bool:
    return any(marker in message for marker in ("HTTP 429", "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504"))


REDACTED_PROVIDER_FIELDS = {
    "thought_signature",
    "thoughtSignature",
    "thinking",
    "reasoning",
    "reasoning_content",
}


def sanitize_raw_response(value):
    """Remove provider-internal reasoning artifacts before writing public JSON."""
    if isinstance(value, dict):
        sanitized = {}
        for key, child in value.items():
            if key in REDACTED_PROVIDER_FIELDS:
                sanitized[key] = "[redacted_provider_internal]"
            else:
                sanitized[key] = sanitize_raw_response(child)
        return sanitized
    if isinstance(value, list):
        return [sanitize_raw_response(item) for item in value]
    return value



def extract_text(response: dict) -> str:
    choices = response.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return str(message.get("content", ""))


def parse_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def build_prompt_manifest(cases: list[dict], modes: list[str], template_dir: Path) -> dict:
    prompts: dict[str, dict[str, str]] = {}
    for mode in modes:
        prompts[mode] = {}
        for case in cases:
            prompts[mode][case["case_id"]] = render_prompt(case, mode, template_dir)
    return prompts


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate CAP LLM dialogue benchmark outputs.")
    parser.add_argument("--base-url", default=os.environ.get("CAP_LLM_BASE_URL", "http://127.0.0.1:1234/v1"))
    parser.add_argument("--api-key-env", default="CAP_LLM_API_KEY")
    parser.add_argument("--models", default=os.environ.get("CAP_BENCH_MODELS", ",".join(DEFAULT_MODELS)))
    parser.add_argument("--modes", default=os.environ.get("CAP_BENCH_MODES", ",".join(DEFAULT_MODES)))
    parser.add_argument("--case-dir", default=str(DEFAULT_CASE_DIR))
    parser.add_argument("--template-dir", default=str(DEFAULT_TEMPLATE_DIR))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=350)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--retries", type=int, default=0)
    parser.add_argument("--retry-delay-seconds", type=float, default=30.0)
    parser.add_argument("--limit-cases", type=int)
    parser.add_argument("--case-ids", help="Comma-separated case ids to run.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-model-check", action="store_true")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing output JSON and skip completed model/mode/case outputs.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.0,
        help="Sleep after each successful generation; useful for free-tier RPM limits.",
    )
    parser.add_argument(
        "--write-partial",
        action="store_true",
        help="Write a checkpoint output JSON after each successful generation.",
    )
    parser.add_argument(
        "--allow-empty-output",
        action="store_true",
        help="Allow empty released message.content. By default empty content is treated as a failed live output.",
    )
    args = parser.parse_args()

    case_dir = Path(args.case_dir).resolve()
    template_dir = Path(args.template_dir).resolve()
    output_json = Path(args.output_json)
    models = parse_csv(args.models, DEFAULT_MODELS)
    modes = parse_csv(args.modes, DEFAULT_MODES)
    cases = filter_cases(load_cases(case_dir, args.limit_cases), parse_csv(args.case_ids, []))
    api_key = os.environ.get(args.api_key_env)

    prompts = build_prompt_manifest(cases, modes, template_dir)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if args.dry_run:
        payload = {
            "kind": "prompt_manifest",
            "generated_at_utc": now,
            "case_dir": str(case_dir.relative_to(ROOT)),
            "template_dir": str(template_dir.relative_to(ROOT)),
            "models": models,
            "modes": modes,
            "prompts": prompts,
        }
        write_json(output_json, payload)
        print(f"Wrote prompt manifest: {output_json}")
        return 0

    available_models: list[str] | None = None
    if not args.skip_model_check:
        available_models = get_available_models(args.base_url, api_key, args.timeout)

    outputs_by_model: dict[str, dict[str, dict[str, str]]] = {}
    run_records: dict[str, dict[str, dict[str, dict]]] = {}
    if args.resume and output_json.exists():
        previous_payload = json.loads(output_json.read_text(encoding="utf-8"))
        outputs_by_model = previous_payload.get("outputs_by_model", {})
        run_records = previous_payload.get("run_records", {})

    for model in models:
        requested_available = None if available_models is None else model in available_models
        if requested_available is False:
            raise SystemExit(
                f"Requested model is not available from /models: {model}. "
                f"Available: {', '.join(available_models or []) or 'none'}"
            )
        outputs_by_model.setdefault(model, {})
        run_records.setdefault(model, {})
        for mode in modes:
            outputs_by_model[model].setdefault(mode, {})
            run_records[model].setdefault(mode, {})
            for case in cases:
                case_id = case["case_id"]
                existing_output = outputs_by_model[model][mode].get(case_id)
                if args.resume and str(existing_output or "").strip():
                    print(f"{model} | {mode} | {case_id} | skip existing")
                    continue
                prompt = prompts[mode][case["case_id"]]
                response = call_chat_completion(
                    args.base_url,
                    model=model,
                    prompt=prompt,
                    api_key=api_key,
                    timeout=args.timeout,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    retries=args.retries,
                    retry_delay_seconds=args.retry_delay_seconds,
                )
                response_model = response.get("model")
                if response_model and response_model != model:
                    raise SystemExit(
                        f"Response model mismatch: requested {model}, got {response_model}"
                    )
                text = extract_text(response)
                if not text.strip() and not args.allow_empty_output:
                    finish_reason = ""
                    choices = response.get("choices", [])
                    if choices:
                        finish_reason = str(choices[0].get("finish_reason", ""))
                    if args.write_partial:
                        write_json(
                            output_json,
                            build_output_payload(
                                now=now,
                                base_url=args.base_url,
                                case_dir=case_dir,
                                template_dir=template_dir,
                                models=models,
                                modes=modes,
                                outputs_by_model=outputs_by_model,
                                run_records=run_records,
                                partial=True,
                                error=(
                                    f"Empty released output: model={model}, mode={mode}, "
                                    f"case={case['case_id']}, finish_reason={finish_reason}"
                                ),
                            ),
                        )
                    raise SystemExit(
                        f"Empty released output: model={model}, mode={mode}, "
                        f"case={case['case_id']}, finish_reason={finish_reason}. "
                        "If this is intentional, rerun with --allow-empty-output."
                    )
                outputs_by_model[model][mode][case["case_id"]] = text
                run_records[model][mode][case["case_id"]] = {
                    "requested_model": model,
                    "response_model": response_model,
                    "model_identity": {
                        "requested_model": model,
                        "identity_check_enforced": not args.skip_model_check,
                        "response_model_check_enforced": True,
                        "requested_model_available": requested_available,
                    },
                    "prompt": prompt,
                    "raw_response": sanitize_raw_response(response),
                }
                print(f"{model} | {mode} | {case['case_id']} | ok")
                if args.write_partial:
                    write_json(
                        output_json,
                        build_output_payload(
                            now=now,
                            base_url=args.base_url,
                            case_dir=case_dir,
                            template_dir=template_dir,
                            models=models,
                            modes=modes,
                            outputs_by_model=outputs_by_model,
                            run_records=run_records,
                            partial=True,
                        ),
                    )
                if args.delay_seconds > 0:
                    time.sleep(args.delay_seconds)

    payload = build_output_payload(
        now=now,
        base_url=args.base_url,
        case_dir=case_dir,
        template_dir=template_dir,
        models=models,
        modes=modes,
        outputs_by_model=outputs_by_model,
        run_records=run_records,
        partial=False,
    )
    write_json(output_json, payload)
    print(f"Wrote model outputs: {output_json}")
    return 0


def build_output_payload(
    *,
    now: str,
    base_url: str,
    case_dir: Path,
    template_dir: Path,
    models: list[str],
    modes: list[str],
    outputs_by_model: dict[str, dict[str, dict[str, str]]],
    run_records: dict[str, dict[str, dict[str, dict]]],
    partial: bool,
    error: str | None = None,
) -> dict:
    payload = {
        "kind": "model_outputs",
        "generated_at_utc": now,
        "base_url": base_url,
        "case_dir": str(case_dir.relative_to(ROOT)),
        "template_dir": str(template_dir.relative_to(ROOT)),
        "models": models,
        "modes": modes,
        "outputs_by_model": outputs_by_model,
        "run_records": run_records,
    }
    if partial:
        payload["partial"] = True
    if error:
        payload["error"] = error
    return payload


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
