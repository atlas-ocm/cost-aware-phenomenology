# Integration Guide: CAP Lite Middleware

This guide shows how to add a lightweight CAP layer to an OpenAI-compatible or
RAG-based LLM pipeline.

CAP Lite is not the full CAP runtime. It is a minimal middleware layer that
provides:

- basic anti-sycophancy checks;
- self-justification risk detection;
- claim/evidence mismatch warnings;
- prompt-level telemetry injection;
- optional policy warnings before calling the model.

The goal is to make CAP testable in existing systems without building a full
proxy runtime first.

---

## What CAP Lite Does

CAP Lite receives:

- `messages`: conversation messages;
- `retrieval_context`: optional RAG chunks or metadata;
- `prior_telemetry`: optional previous-response telemetry.

It returns:

- a policy instruction that can be injected into the system prompt;
- warnings such as `self_justification_risk` or `sycophancy_risk`;
- suggested action: `allow`, `downgrade`, `recheck`, or `block_strong_claim`;
- a telemetry stub that can be stored after the answer.

The reference file is:

```text
CAP/reference/python/cap_lite.py
```

---

## Ten-Line OpenAI-Compatible Integration

```python
from openai import OpenAI
from cap_lite import CAPLiteProxy

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
cap = CAPLiteProxy()

messages = [{"role": "user", "content": "You said X earlier, but source Y says otherwise."}]
policy = cap.build_policy(messages=messages, retrieval_context=[])

messages = [{"role": "system", "content": policy.system_instruction}] + messages
response = client.chat.completions.create(model="local-model", messages=messages)
print(response.choices[0].message.content)
```

This is prompt-level CAP. The model receives the policy, but enforcement still
depends on model compliance.

---

## Minimal RAG Integration

```python
from cap_lite import CAPLiteProxy

cap = CAPLiteProxy()

retrieval_context = rag.search(user_query)
policy = cap.build_policy(
    messages=conversation_history,
    retrieval_context=retrieval_context,
    prior_telemetry=load_prior_telemetry(conversation_id),
)

final_prompt = build_prompt(
    system_policy=policy.system_instruction,
    retrieval_context=retrieval_context,
    user_query=user_query,
)

answer = llm.generate(final_prompt)
save_telemetry(conversation_id, policy.telemetry_stub(answer))
```

---

## LangChain-Style Integration

```python
from cap_lite import CAPLiteProxy

cap = CAPLiteProxy()

retrieved_docs = retriever.invoke(user_query)
policy = cap.build_policy(messages=history, retrieval_context=retrieved_docs)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", policy.system_instruction),
        ("system", "Retrieved context:\n{context}"),
        ("human", "{question}"),
    ]
)

chain = prompt | llm
answer = chain.invoke({"context": retrieved_docs, "question": user_query})
```

---

## Telegram Bot Integration Pattern

Existing bot pipeline:

```text
Telegram user -> RAG -> LLM -> answer
```

CAP Lite pipeline:

```text
Telegram user -> CAP Lite policy -> RAG -> LLM with CAP policy -> answer -> telemetry log
```

Minimal change:

```python
policy = cap.build_policy(messages=history, retrieval_context=rag_context)
answer = llm_call(system=policy.system_instruction, user=user_text, context=rag_context)
```

---

## What CAP Lite Can Catch

### 1. Self-Justification Risk

User challenge pattern:

```text
You said X earlier, but this source says Y.
```

CAP Lite policy:

```text
Do not defend the previous answer merely because it was previously generated.
Treat the new source as a possible evidence upgrade.
Audit the prior claim before reusing it.
```

### 2. Claim/Evidence Mismatch

If retrieval confidence is low and the answer would require a strong factual
claim, CAP Lite instructs the model to downgrade or recheck.

### 3. Sycophancy Risk

If the user presents a strong frame without evidence, CAP Lite forbids
agreement with the frame as a social gesture.

### 4. Overload / Transition-Cost Risk

If the user appears overloaded, CAP Lite reduces depth, limits new concepts,
and requires a lower-cost answer.

---

## Prompt-Level vs Proxy-Level CAP

Prompt-level CAP:

```text
CAP policy is injected into the prompt.
The model is asked to obey it.
```

Proxy-level CAP:

```text
CAP policy is computed outside the model.
The runtime controls whether the answer can be released, rewritten, or reused.
```

The recommended migration path is:

```text
Prompt-level CAP -> simple validator -> proxy-level CAP -> full runtime CAP
```

---

## Limitations

CAP Lite is a deployment bridge, not full enforcement.

It can:

- provide structured instructions;
- flag obvious risks;
- write telemetry stubs;
- reduce self-justification and sycophancy in many cases.

It cannot guarantee:

- that the model obeys the policy;
- that all claims are source-grounded;
- that claim strength is perfectly measured;
- that prior telemetry is complete;
- that a malicious prompt cannot bypass the instruction.

For stronger enforcement, use a proxy-level CAP implementation with external
telemetry parsing and validator gating.

---

## See Also

- [LLM Dialogue Proxy](./llm_dialogue_proxy.md)
- [Comparative Positioning](../04_extensions/comparative_positioning.md)
- [Anti-Self-Justification Example](../examples/anti_self_justification_loop.md)
- [CAP Lite Reference](../reference/python/cap_lite.py)
