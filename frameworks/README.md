# Use ZaFeed from a web application

These six examples call the ZaFeed v1 REST API from application code. Each solves a different integration problem and runs against a local HTTP fixture before you add a market Key. Run a single example at a time while learning the API.

六个示例分别处理自选股、东京交易日、快照分页、多市场鉴权、限流和报价回退。运行本地演示只需要对应语言环境和 Python 3，无需真实 Key。

| Example | Problem it solves |
| --- | --- |
| [Express watchlist](express/) | Keep browser code free of market Keys and keep missing quotes in the list |
| [FastAPI Tokyo candles](fastapi/) | Map a candle timestamp to the date in Tokyo without filling closed sessions |
| [Go net/http snapshot](go-net-http/) | Follow an opaque HKEX pagination cursor and stop on a repeated cursor |
| [Spring Boot market keys](spring-boot/) | Choose the correct server-side Key for US and Hong Kong requests |
| [ASP.NET Core backoff](aspnet-core/) | Forward an upstream 429 with a usable Retry-After delay |
| [Laravel last known quote](laravel/) | Label a cached quote during a brief upstream outage |

Start the fixture from the repository root:

```bash
python3 frameworks/mock-zafeed.py
```

Open a second terminal and follow one example's instructions. Ports 8099 and 8101–8106 are loopback only. The fixture checks the market-specific demo Keys and uses synthetic prices. Restart it to reset the Laravel outage sequence.

For your own service, set `ZAFEED_BASE_URL` to the assigned HTTPS origin and replace the relevant demo Key in the server environment. The examples bind to loopback. Add your application's authentication and authorization before exposing any routes to clients. The [ZaFeed REST quickstart](https://www.zafeed.com/docs-guide.html) describes the production API, while the [symbol directory](https://www.zafeed.com/symbols.html) provides the identifiers to request.
