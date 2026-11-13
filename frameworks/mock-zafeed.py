"""Local ZaFeed v1 fixture. All prices, keys, and responses are synthetic."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from urllib.parse import parse_qs, urlsplit


class DemoAPI(BaseHTTPRequestHandler):
    lock = Lock()
    card_requests = 0

    def send_json(self, status, payload, retry_after=None):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if retry_after is not None:
            self.send_header("Retry-After", str(retry_after))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        params = parse_qs(url.query)
        market = params.get("market", [""])[0]
        if market not in {"US", "JP", "HK"} or self.headers.get("X-API-Key") != f"demo-{market.lower()}":
            return self.send_json(403, {"error": {"code": "market_forbidden"}})
        if url.path == "/v1/klines" and market == "JP":
            symbol = params.get("symbol", [""])[0]
            if symbol not in {"TSE:7203", "TSE:130A"}:
                return self.send_json(404, {"error": {"code": "symbol_not_found"}})
            if params.get("interval") != ["1d"]:
                return self.send_json(400, {"error": {"code": "invalid_param"}})
            bar = dict(time=1767628800000, open=100, high=105, low=98, close=102, volume=3200)
            return self.send_json(200, {"data": {"symbol": symbol, "interval": "1d", "bars": [bar]}})
        if url.path == "/v1/snapshot" and market == "HK" and params.get("venue") == ["HKEX"]:
            cursor = params.get("cursor", [None])[0]
            if cursor not in {None, "next+/=page"}:
                return self.send_json(400, {"error": {"code": "invalid_param"}})
            symbol, next_page = ("HKEX:00700", "next+/=page") if cursor is None else ("HKEX:00005", None)
            return self.send_json(200, {"data": [dict(symbol=symbol, price=100)], "meta": {"next": next_page}})
        if url.path == "/v1/quotes":
            symbols = params.get("symbols", [""])[0].split(",")
            if market == "US" and symbols == ["NASDAQ:RATE"]:
                return self.send_json(429, {"error": {"code": "rate_limited"}}, retry_after=7)
            if market == "HK" and symbols == ["HKEX:00700"]:
                with self.lock:
                    type(self).card_requests += 1
                    first = self.card_requests == 1
                if not first:
                    return self.send_json(503, {"error": {"code": "unavailable"}})
            known = {"US": {"NASDAQ:AAPL", "NYSE:JPM"}, "HK": {"HKEX:00700", "HKEX:00005"}, "JP": set()}
            return self.send_json(200, {"data": [
                {"symbol": symbol, "price": 100, "time": 1767628800000}
                for symbol in symbols if symbol in known[market]
            ]})
        return self.send_json(404, {"error": {"code": "not_found"}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), DemoAPI) as server:
        print(f"Fixture listening at http://127.0.0.1:{args.port}", flush=True)
        server.serve_forever()
