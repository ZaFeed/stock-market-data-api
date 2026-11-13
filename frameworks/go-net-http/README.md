# Read a paginated HKEX snapshot with Go net/http

The handler follows `meta.next` across snapshot pages. It sends each cursor back as an opaque query value, uses a shared deadline, and returns an error if the cursor repeats or the page budget runs out. This keeps an incomplete snapshot from replacing the previous one.

With the [fixture running](../README.md), use Go 1.22 or later:

```bash
cd frameworks/go-net-http
ZAFEED_BASE_URL=http://127.0.0.1:8099 ZAFEED_HK_KEY=demo-hk go run main.go
```

```bash
curl http://127.0.0.1:8103/hkex/snapshot
```

The fixture returns `HKEX:00700` and `HKEX:00005` on separate pages. Its cursor contains `+`, `/` and `=` to demonstrate URL encoding. Adjust the page budget for your application and refer to the [snapshot API](https://www.zafeed.com/docs-exchange.html) for page limits.
