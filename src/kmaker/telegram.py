"""Send a short text digest to Telegram. A no-op when credentials are absent."""

from __future__ import annotations

import logging

import httpx

log = logging.getLogger(__name__)


def send(token: str, chat_id: str, text: str) -> bool:
    if not token or not chat_id:
        return False
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": True},
            timeout=20,
        )
        r.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        # not the exception text: it quotes the URL, which holds the token
        status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else ""
        log.warning("telegram send failed: %s %s", type(exc).__name__, status)
        return False
