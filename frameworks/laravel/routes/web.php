<?php

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Route;

Route::get('/tencent/quote-card', function () {
    $origin = rtrim((string) env('ZAFEED_BASE_URL'), '/');
    $key = (string) env('ZAFEED_HK_KEY');
    $parts = parse_url($origin);
    $scheme = $parts['scheme'] ?? '';
    $host = $parts['host'] ?? '';
    if ($host === '' || isset($parts['user']) || isset($parts['pass']) ||
        isset($parts['path']) || isset($parts['query']) || isset($parts['fragment']) || $key === '' ||
        ($scheme !== 'https' && !($scheme === 'http' && $host === '127.0.0.1'))) {
        return response()->json(['error' => 'Set ZAFEED_BASE_URL and ZAFEED_HK_KEY.'], 500);
    }

    $symbol = 'HKEX:00700';
    $cacheKey = 'quote-card:'.hash('sha256', $origin."\n".$key."\n".$symbol);
    $upstreamStatus = null;
    try {
        $reply = Http::acceptJson()->withHeaders(['X-API-Key' => $key])
            ->withoutRedirecting()->timeout(5)->get($origin.'/v1/quotes', [
                'market' => 'HK', 'symbols' => $symbol,
            ]);
        $upstreamStatus = $reply->status();
        if ($reply->successful()) {
            $quote = collect($reply->json('data', []))->firstWhere('symbol', $symbol);
            if ($quote === null) {
                Cache::forget($cacheKey);
                return response()->json(['error' => 'Quote unavailable for this symbol.'], 404);
            }
            $record = ['quote' => $quote, 'fetchedAt' => now()->toIso8601String()];
            Cache::put($cacheKey, $record, 120);
            return response()->json($record + ['stale' => false]);
        }
    } catch (ConnectionException) {
        // Network timeouts use the same fallback as upstream 5xx responses.
    }

    if ($upstreamStatus === null || $upstreamStatus >= 500) {
        $record = Cache::get($cacheKey);
        if ($record !== null) {
            return response()->json($record + ['stale' => true]);
        }
        return response()->json(['error' => 'Quote service unavailable.'], 503);
    }

    return response()->json(['error' => 'Quote request failed.', 'upstreamStatus' => $upstreamStatus], 502);
});
