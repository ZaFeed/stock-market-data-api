# Global Stock Market Data API Examples

**全球股票行情 API 接入示例**

ZaFeed issues one API Key per market. REST requests use the market code and exchange-qualified symbols such as `NASDAQ:AAPL`, `HKEX:00700` and `TSE:7203`.

Global stock quotes, OHLC history, exchange snapshots and WebSocket examples through ZaFeed. This repository contains client examples for the ZaFeed API, with public catalog lookups and authenticated REST requests.

[ZaFeed 官网](https://www.zafeed.com/) · [API Quick Start](https://www.zafeed.com/docs-guide.html) · [Markets & Pricing](https://www.zafeed.com/pricing.html) · [Symbol Directory](https://www.zafeed.com/symbols.html) · [Trading Calendar](https://www.zafeed.com/calendar.html)

## Market and exchange index · 市场与交易所索引

| Market | Code | Exchanges in the public catalog | Sample symbols |
| --- | --- | --- | --- |
| Australia · 澳大利亚 | `AU` | ASX | `ASX:BHP` |
| Brazil · 巴西 | `BR` | B3 | See the symbol directory |
| Canada · 加拿大 | `CA` | TSX, TSXV | See the symbol directory |
| Switzerland · 瑞士 | `CH` | SIX | See the symbol directory |
| Mainland China · 中国大陆 | `CN` | SSE, SZSE, BSE | `SZSE:300750`, `SSE:600519` |
| Germany · 德国 | `DE` | XETR, FWB | `XETR:SAP`, `XETR:SIE` |
| France · 法国 | `FR` | EURONEXT | `EURONEXT:MC` |
| United Kingdom · 英国 | `GB` | LSE | `LSE:AZN`, `LSE:SHEL` |
| Hong Kong · 中国香港 | `HK` | HKEX | `HKEX:00005`, `HKEX:00700` |
| India · 印度 | `IN` | NSE, BSE | `NSE:RELIANCE`, `NSE:TCS` |
| Japan · 日本 | `JP` | TSE, OSE | `TSE:6758`, `TSE:7203` |
| South Korea · 韩国 | `KR` | KRX | `KRX:000660`, `KRX:005930` |
| Mexico · 墨西哥 | `MX` | BMV, BIVA | See the symbol directory |
| Saudi Arabia · 沙特阿拉伯 | `SA` | TADAWUL | `TADAWUL:2222` |
| Singapore · 新加坡 | `SG` | SGX | See the symbol directory |
| Taiwan · 中国台湾 | `TW` | TWSE, TPEX | `TWSE:2330` |
| United States · 美国 | `US` | NASDAQ, NYSE, AMEX | `NASDAQ:AAPL`, `NASDAQ:AMZN` |
| South Africa · 南非 | `ZA` | JSE | See the symbol directory |

The public catalog contains market listings. Exchange availability, credentials and endpoint access are confirmed through the ZaFeed site.

## Run a public catalog request · 无需 Key 查询标的

| Language | Run |
| --- | --- |
| Python 3 | `python3 market_data.py catalog` |
| Node.js 22+ | `node market-data.mjs catalog` |
| Go | `go run market_data.go catalog` |
| Java 17+ | `java MarketData.java catalog` |
| cURL | `bash market-data.sh catalog` |

Python, Node.js and Go filter the public response by market. Java and cURL print the full public response. The catalog returns sample symbol metadata.

## Connect to quotes, candles and exchange snapshots · 连接行情接口

Set `ZAFEED_HTTP_BASE_URL` to the HTTPS origin assigned for your data service, and `ZAFEED_API_KEY` to a Key for the selected market. The scripts default to `US` and `NASDAQ:AAPL`. Set `ZAFEED_MARKET` and `ZAFEED_SYMBOL` together when switching markets.

```bash
python3 market_data.py quotes
node market-data.mjs klines
go run market_data.go snapshot
java MarketData.java quotes
bash market-data.sh klines
```

- [Stock quotes API](https://www.zafeed.com/docs-quote.html) uses `symbols` for a comma-separated list.
- [Historical OHLC API](https://www.zafeed.com/docs-kline.html) uses `symbol`, `interval` and `limit`.
- [Exchange snapshot API](https://www.zafeed.com/docs-exchange.html) can filter by `venue` and returns a pagination cursor when available.

## Subscribe with WebSocket · WebSocket 订阅

Set `ZAFEED_WS_BASE_URL` to your assigned `wss://` origin and use the same market Key.

```bash
node market-data.mjs stream
```

The example waits for `welcome`, sends `subscribe`, and reads messages for up to 15 seconds. A subscription acknowledgement can arrive before a quote update. See the [WebSocket protocol](https://www.zafeed.com/docs-ws.html).

**Availability · 接入状态:** The public catalog commands were checked against ZaFeed. Authenticated REST and WebSocket require a provisioned data service endpoint and matching market Key. 实时报价、历史 K 线和推送需要已开通的接口地址及对应市场 Key。

**Support · 技术支持:** [support@zafeed.net](mailto:support@zafeed.net)
