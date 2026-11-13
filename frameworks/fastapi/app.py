import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, HTTPException, Query

TOKYO = ZoneInfo("Asia/Tokyo")
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


@asynccontextmanager
async def lifespan(app):
    origin = os.environ["ZAFEED_BASE_URL"].rstrip("/")
    base = urlsplit(origin)
    key = os.environ["ZAFEED_JP_KEY"]
    if (
        not base.hostname or base.username is not None or base.path or base.query or base.fragment
        or (base.scheme != "https" and not (base.scheme == "http" and base.hostname == "127.0.0.1"))
        or not key
    ):
        raise RuntimeError("Set a trusted HTTPS origin (or the loopback demo) and a Japan market key.")
    async with httpx.AsyncClient(
        base_url=origin, headers={"X-API-Key": key}, timeout=5.0, follow_redirects=False
    ) as client:
        app.state.upstream = client
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/tokyo/candles")
async def candles(
    symbol: Annotated[str, Query(pattern=r"^TSE:[A-Z0-9]{4}$")] = "TSE:7203",
    limit: Annotated[int, Query(ge=1, le=1000)] = 30,
):
    try:
        reply = await app.state.upstream.get(
            "/v1/klines", params={"market": "JP", "symbol": symbol, "interval": "1d", "limit": limit}
        )
        if reply.status_code == 404:
            raise HTTPException(404, "Unknown Tokyo symbol")
        reply.raise_for_status()
        bars = reply.json()["data"]["bars"]
        return {
            "symbol": symbol, "timeZone": TOKYO.key,
            "bars": [
                {**bar, "sessionDate": (EPOCH + timedelta(milliseconds=bar["time"])).astimezone(TOKYO).date().isoformat()}
                for bar in bars
            ],
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError, OverflowError) as exc:
        raise HTTPException(502, "Candle service unavailable or returned invalid data") from exc
