"""Server-side Google Analytics 4 purchase events (Measurement Protocol).

Sent from Stripe fulfillment, so every paid checkout reaches GA — even when the
buyer closes the tab before the success page loads or blocks gtag.js.

Config (env):
  GA_API_SECRET      — GA Admin → Data streams → (soulscript stream) →
                       Measurement Protocol API secrets. Unset = disabled (no-op).
  GA_MEASUREMENT_ID  — defaults to the soulscript.orionforge.chat stream.
"""

import hashlib
import logging
import os
import re
import threading
import time

import requests

log = logging.getLogger("soulscript.ga")

GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "G-2SCFQ9V4MW")
GA_API_SECRET = os.environ.get("GA_API_SECRET", "")
_MP_URL = "https://www.google-analytics.com/mp/collect"


def ga_ids_from_cookies(cookies) -> dict:
    """GA client/session ids from the buyer's cookies, for Stripe checkout metadata.

    Lets the server-side purchase join the buyer's real GA session, so revenue is
    attributed to the traffic source (Reddit ad, organic, ...) that brought them.
    """
    out = {}
    parts = (cookies.get("_ga") or "").split(".")  # GA1.1.<random>.<timestamp>
    if len(parts) >= 4:
        out["ga_client_id"] = ".".join(parts[-2:])
    # GS1.1.<session_id>.… (old format) or GS2.1.s<session_id>$o1$… (new format)
    session_cookie = cookies.get("_ga_" + GA_MEASUREMENT_ID.removeprefix("G-")) or ""
    m = re.match(r"GS\d\.\d\.s?(\d+)", session_cookie)
    if m:
        out["ga_session_id"] = m.group(1)
    return out


def send_purchase(*, transaction_id: str, value: float, currency: str, user_id: str,
                  item_id: str, item_name: str, credits: int,
                  client_id: str = "", session_id: str = "") -> bool:
    """Queue a GA4 `purchase` event. Returns False when disabled or incomplete."""
    if not GA_API_SECRET or not transaction_id:
        return False
    if not client_id:
        # No _ga cookie (blocked / never loaded): use a stable per-user id so the
        # revenue still counts, just without session attribution.
        digest = int(hashlib.sha256((user_id or transaction_id).encode()).hexdigest()[:9], 16)
        client_id = f"{digest}.{int(time.time())}"
    params = {
        "transaction_id": transaction_id,
        "value": round(value, 2),
        "currency": currency.upper(),
        "items": [{
            "item_id": item_id,
            "item_name": item_name,
            "item_category": "credits",
            "price": round(value, 2),
            "quantity": 1,
        }],
        "credits": credits,
        "engagement_time_msec": 1,
    }
    if session_id:
        params["session_id"] = session_id
    body = {"client_id": client_id, "events": [{"name": "purchase", "params": params}]}
    if user_id:
        body["user_id"] = user_id
    # Off the request path: a slow GA endpoint must never delay a Stripe webhook.
    threading.Thread(target=_post, args=(body,), daemon=True).start()
    return True


def _post(body: dict) -> None:
    try:
        resp = requests.post(
            _MP_URL,
            params={"measurement_id": GA_MEASUREMENT_ID, "api_secret": GA_API_SECRET},
            json=body,
            timeout=10,
        )
        if resp.status_code >= 300:
            log.warning("[ga] purchase event rejected (%s): %s", resp.status_code, resp.text[:200])
        else:
            log.info("[ga] purchase sent: %s", body["events"][0]["params"]["transaction_id"])
    except Exception as exc:
        log.warning("[ga] purchase event failed: %s", exc)
