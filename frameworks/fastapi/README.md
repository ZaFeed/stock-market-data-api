# Put Tokyo daily candles on the correct date with FastAPI

ZaFeed returns the start time of each candle in Unix milliseconds. This route adds a `sessionDate` in `Asia/Tokyo` and retains the timestamp and OHLCV fields. A candle can belong to Tuesday in Japan while its UTC date is Monday.

With the [fixture running](../README.md), use Python 3.11 or later:

```bash
cd frameworks/fastapi
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
ZAFEED_BASE_URL=http://127.0.0.1:8099 ZAFEED_JP_KEY=demo-jp \
  .venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8102
```

```bash
curl -G http://127.0.0.1:8102/tokyo/candles \
  --data-urlencode 'symbol=TSE:7203' --data-urlencode 'limit=30'
```

The fixture candle has timestamp `1767628800000` and session date `2026-01-06`. The route also accepts identifiers such as `TSE:130A`. It returns only bars supplied by the [historical candles API](https://www.zafeed.com/docs-kline.html).
