import express from "express";

const base = new URL(process.env.ZAFEED_BASE_URL ?? "");
const key = process.env.ZAFEED_US_KEY;
if ((base.protocol !== "https:" && !(base.protocol === "http:" && base.hostname === "127.0.0.1"))
    || base.username || base.password || base.href !== base.origin + "/" || !key) {
  throw new Error("Set ZAFEED_BASE_URL to an HTTPS origin (or the loopback demo) and ZAFEED_US_KEY.");
}

const app = express();
app.get("/watchlist", async (req, res) => {
  const raw = req.query.symbols;
  const symbols = typeof raw === "string" && raw.length <= 4000
    ? [...new Set(raw.toUpperCase().split(",").map(s => s.trim()))] : [];
  if (!symbols.length || symbols.length > 50
      || symbols.some(s => !/^[A-Z0-9_]{1,24}:[A-Z0-9._&!\-]{1,48}$/.test(s))) {
    return res.status(400).json({error: "Provide 1–50 exchange-qualified US symbols."});
  }

  const url = new URL("/v1/quotes", base);
  url.search = new URLSearchParams({market: "US", symbols: symbols.join(",")});
  try {
    const upstream = await fetch(url, {
      headers: {"X-API-Key": key}, redirect: "error", signal: AbortSignal.timeout(5000)
    });
    if (!upstream.ok) return res.status(502).json({error: "Quote request failed", upstreamStatus: upstream.status});
    const {data} = await upstream.json();
    const quotes = new Map(data.map(quote => [quote.symbol, quote]));
    res.json({rows: symbols.map(symbol => ({symbol, quote: quotes.get(symbol) ?? null}))});
  } catch {
    res.status(502).json({error: "Quote service unavailable"});
  }
});

app.listen(Number(process.env.PORT ?? 8101), "127.0.0.1");
