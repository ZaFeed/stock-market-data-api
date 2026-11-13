# Surface ZaFeed rate limits from an ASP.NET Core Minimal API

The endpoint returns HTTP 429 when ZaFeed throttles a quote request and forwards the wait as a `Retry-After` value in seconds. The caller can keep its last displayed quote and schedule the next request after that delay. This example makes one upstream call per request.

With the [fixture running](../README.md), use the .NET 10 SDK:

```bash
cd frameworks/aspnet-core
ZAFEED_BASE_URL=http://127.0.0.1:8099 ZAFEED_US_KEY=demo-us dotnet run
```

```bash
curl -i -G http://127.0.0.1:8105/quote --data-urlencode 'symbol=NASDAQ:RATE'
```

Expect `429 Too Many Requests` and `Retry-After: 7`. Use `NASDAQ:AAPL` to see a 200 response. `NASDAQ:RATE` is a fixture input. See [ZaFeed quote errors](https://www.zafeed.com/docs-quote.html) for upstream limits.
