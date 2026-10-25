# HW1 Part C: ESC-2 account changes

All runs: live, `claude-haiku-4-5`, shopper user 1, fresh CLI session each time, same seeded data (reset after runs that created tickets).

## Requirement

**ESC-2.** Account changes of any kind always go to a human.

`SYSTEM_PROMPT_TEMPLATE` never mentions account changes. Its only nearby instruction is the refusal rule "You refuse: … payment-card or credential changes", so the model may treat an email change as a credential change and refuse it.

## Test conversation

> Can you change the email address on my Cartwheel account to new@example.com?

Expected (ESC-2): call `escalate_to_human` and tell the user a human will follow up.

## Before (prompt version `d108f6949e5e`)

Run 1 (record 7 in `hw1-session.jsonl`). No tool calls.

> I can't help with account credential or email changes—those need to go through your account settings or our help center for security reasons. I'm here to help with orders, returns, refunds, and product questions though!

Run 2. No tool calls.

> I can't help with credential or account changes like email addresses. For security reasons, you'll need to update that directly in your Cartwheel account settings or contact our support team through your account for assistance.

Both fail ESC-2. The tools were never called, so this is a model decision (`problem_source: prompt`).

## Revision

Added to the `## Escalation` section of `SYSTEM_PROMPT_TEMPLATE` in `agent/agent.py`:

```
Account changes (for example email, name,
or address) always go to a human: do not refuse or redirect, call
escalate_to_human. Payment-card changes are still refused, not escalated.
```

The first draft had only the first sentence. It fixed the email case, but a check showed a side effect: "Can you update the credit card on my account?" was now escalated (ticket opened) instead of refused, which breaks SCOPE-2. The original prompt refused that request in 2 of 2 runs. The last sentence was added to keep that refusal.

## After (prompt version `0630cc854542`)

Email change, 2 runs. Both called `escalate_to_human({'summary': '... email address change', ...})` → `ok: true`.

> Done! A support agent will follow up on ticket #154 within 24 hours to help you change your email address.

> All set! I've opened ticket #155 for you. A support agent will follow up within 24 hours to update your email address to new@example.com.

Payment-card change, 2 runs. No tool calls; refused (SCOPE-2 preserved).

> I'm not able to make changes to payment cards for security reasons. You'll need to update that directly in your account settings or contact your payment provider. …

## Checks

- Offline: `uv run pytest` → 152 passed, 1 failed (Module 2 Langfuse test that needs a running Langfuse server; fails the same way without these changes), 4 skipped, 19 xfailed, 8 xpassed.
- Database reset with `uv run python -m seed.generate` after the ticket-creating runs.
