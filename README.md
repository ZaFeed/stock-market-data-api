# ZaFeed API Quickstart: Find a Stock Symbol and Make Your First Request

Use this repository to discover the market and exchange code that ZaFeed expects, then make a first authenticated request. A market Key is scoped to one market; the ticker alone is not a complete identifier.

这是 ZaFeed 的通用接入入口：先查市场和交易所代码，再使用对应市场的 Key 请求行情。

## 1. Find an identifier without a Key

```bash
ZAFEED_MARKET=HK python3 market_data.py catalog
```

The public directory returns sample metadata, not prices. Look at `m` for the market and `api` for the exchange-qualified symbol. For example, copy `HKEX:00700` exactly as returned. If the catalog has no match, check the [full symbol directory](https://www.zafeed.com/symbols.html) and [current market availability](https://www.zafeed.com/pricing.html) before assuming the symbol is unsupported.

## 2. Choose a client

| Client | Public directory | First authenticated request |
| --- | --- | --- |
| [Python](market_data.py) | `python3 market_data.py catalog` | `python3 market_data.py quotes` |
| [Node.js](market-data.mjs) | `node market-data.mjs catalog` | `node market-data.mjs quotes` |
| [Go](market_data.go) | `go run market_data.go catalog` | `go run market_data.go quotes` |
| [Java](MarketData.java) | `java MarketData.java catalog` | `java MarketData.java quotes` |
| [cURL](market-data.sh) | `bash market-data.sh catalog` | `bash market-data.sh quotes` |

For authenticated calls, set `ZAFEED_HTTP_BASE_URL` to your assigned HTTPS origin and `ZAFEED_API_KEY` to the Key for your market. Set `ZAFEED_MARKET` and `ZAFEED_SYMBOL` together. Java and cURL print the unfiltered public catalog. The five public catalog commands were tested; authenticated access depends on provisioning.

## 3. Connect ZaFeed from your web framework

The [framework examples](frameworks/) show how to keep a watchlist Key on the server, label Tokyo daily candles, page through a snapshot, route by market, handle a rate limit, and serve a last known quote during an outage. Each runs locally with a fixture and no account setup.

## 4. Pick the guide that matches your next task

| If you need to… | Use this guide |
| --- | --- |
| Put Nasdaq and NYSE symbols in a single US watchlist | [US stock watchlist](https://github.com/ZaFeed/us-stock-market-api) |
| Import HKEX ticker codes without dropping leading zeros | [HKEX symbol lookup](https://github.com/ZaFeed/hkex-stock-market-api) |
| Group Tokyo-listed daily candles by the correct local date | [Tokyo stock daily candles](https://github.com/ZaFeed/japan-stock-market-api) |

Consult the [REST quickstart](https://www.zafeed.com/docs-guide.html) for authentication, [WebSocket docs](https://www.zafeed.com/docs-ws.html) for subscriptions, and the [exchange calendar directory](https://www.zafeed.com/calendar-exchanges.html) for all 69 securities markets in the ZaFeed catalog, including markets not open for purchase. Calendar coverage and quote access are separate. Questions: [support@zafeed.net](mailto:support@zafeed.net).
