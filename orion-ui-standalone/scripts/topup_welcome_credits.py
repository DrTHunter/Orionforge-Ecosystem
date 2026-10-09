"""One-time top-up: bring existing users' welcome grant up to the current amount.

Users who signed up under an older, smaller welcome grant get the difference
(e.g. $2 -> $5 adds 3,000 credits). Idempotent: each user is topped up at most
once per target amount, tracked by the history reason.

Dry run by default. On the Fly machine:
    python -m scripts.topup_welcome_credits            # show what would change
    python -m scripts.topup_welcome_credits --apply    # do it
"""
from __future__ import annotations

import re
import sys

from web.stripe_billing import (
    CREDITS_PER_USD, WELCOME_CREDITS, _load_stripe_state, add_user_credits,
)

_GRANT_RE = re.compile(r"^welcome_grant:new_user_\$(\d+)$")


def main(apply: bool) -> None:
    target_usd = WELCOME_CREDITS // CREDITS_PER_USD
    topup_reason = f"welcome_topup:to_${target_usd}"
    state = _load_stripe_state()

    plan: list[tuple[str, int]] = []
    for uid, bucket in state.get("credits", {}).items():
        history = bucket.get("history", [])
        if any(h.get("reason") == topup_reason for h in history):
            continue  # already topped up to this amount
        granted_usd = [int(m.group(1)) for h in history
                       if (m := _GRANT_RE.match(str(h.get("reason", ""))))]
        if not granted_usd:
            continue  # never received a welcome grant
        missing = WELCOME_CREDITS - max(granted_usd) * CREDITS_PER_USD
        if missing > 0:
            plan.append((uid, missing))

    for uid, amount in plan:
        print(f"{'+' if apply else 'would add '}{amount:>6} credits  {uid}")
        if apply:
            add_user_credits(uid, amount, reason=topup_reason)
    total = sum(a for _, a in plan)
    print(f"\n{len(plan)} users, {total} credits (${total / CREDITS_PER_USD:,.2f})"
          f"{'' if apply else '  — dry run, pass --apply to grant'}")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
