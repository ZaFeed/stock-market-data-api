# Keep a quote card available during a short outage with Laravel

The first successful Tencent quote is stored for two minutes. A transport error or upstream 5xx response can use that last known quote with `stale: true` and its original `fetchedAt`. Your UI can show the age instead of displaying the old price as fresh. Authentication errors and rate limits produce an error response.

With a freshly started [fixture](../README.md), use PHP 8.3 or later, Composer 2 and the PHP extensions required by Laravel:

```bash
cd frameworks/laravel
composer install
mkdir -p storage/framework/cache/data bootstrap/cache
ZAFEED_BASE_URL=http://127.0.0.1:8099 ZAFEED_HK_KEY=demo-hk \
  php -S 127.0.0.1:8106 -t public public/index.php
```

```bash
curl http://127.0.0.1:8106/tencent/quote-card
curl http://127.0.0.1:8106/tencent/quote-card
```

Run both commands within two minutes. The first response contains `stale: false`. The fixture returns a 503 to the second upstream request, so the app returns `stale: true` and the same `fetchedAt`. A cold cache during an outage returns 503. This uses Laravel's [HTTP client](https://laravel.com/docs/13.x/http-client) and local file cache.
