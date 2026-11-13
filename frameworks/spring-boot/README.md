# Route US and HK quote requests to the right Key in Spring Boot

A ZaFeed Key belongs to one market. The controller maps the requested market to its server-side Key and checks that the symbol belongs to the same market before calling ZaFeed. The request does not carry the upstream Key or origin.

With the [fixture running](../README.md), use JDK 21 and Maven:

```bash
cd frameworks/spring-boot
ZAFEED_BASE_URL=http://127.0.0.1:8099 ZAFEED_US_KEY=demo-us ZAFEED_HK_KEY=demo-hk \
  mvn spring-boot:run
```

```bash
curl -G http://127.0.0.1:8104/quotes/US --data-urlencode 'symbol=NYSE:JPM'
curl -G http://127.0.0.1:8104/quotes/HK --data-urlencode 'symbol=HKEX:00005'
curl -i -G http://127.0.0.1:8104/quotes/US --data-urlencode 'symbol=HKEX:00005'
```

The first two calls return quotes. The third returns 400 locally. In a larger service, use a secret manager for the market keys and keep the [market-scoped authorization rules](https://www.zafeed.com/docs-auth.html) at the boundary.
