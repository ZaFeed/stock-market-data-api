# Serve a US stock watchlist from Express

The browser sends exchange-qualified symbols to Express. Express attaches the US market Key on the server, requests a single batch from ZaFeed, and joins quotes back to the original watchlist order. A missing quote becomes `null` so the UI can keep the row visible.

With the [fixture running](../README.md), use Node.js 22 or later:

```bash
cd frameworks/express
npm ci
ZAFEED_BASE_URL=http://127.0.0.1:8099 ZAFEED_US_KEY=demo-us npm start
```

```bash
curl -G http://127.0.0.1:8101/watchlist \
  --data-urlencode 'symbols=NYSE:JPM,NASDAQ:AAPL,NASDAQ:UNKNOWN'
```

The response keeps JPM, AAPL, then UNKNOWN. UNKNOWN has `quote: null`. The endpoint validates up to 50 distinct symbols and makes one [quotes request](https://www.zafeed.com/docs-quote.html).
