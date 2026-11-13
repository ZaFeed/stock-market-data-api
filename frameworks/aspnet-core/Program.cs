using System.Globalization;
using System.Net;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.WebUtilities;

var builder = WebApplication.CreateBuilder(args);
var configured = Environment.GetEnvironmentVariable("ZAFEED_BASE_URL");
var key = Environment.GetEnvironmentVariable("ZAFEED_US_KEY");
if (!Uri.TryCreate(configured, UriKind.Absolute, out var origin) || origin.Host.Length == 0
    || origin.UserInfo.Length > 0 || origin.AbsolutePath != "/" || origin.Query.Length > 0 || origin.Fragment.Length > 0
    || (origin.Scheme != "https" && !(origin.Scheme == "http" && origin.Host == "127.0.0.1"))
    || string.IsNullOrWhiteSpace(key))
{
    throw new InvalidOperationException("Set ZAFEED_BASE_URL and ZAFEED_US_KEY.");
}

builder.WebHost.UseUrls("http://127.0.0.1:" + (Environment.GetEnvironmentVariable("PORT") ?? "8105"));
builder.Services.AddHttpClient("zafeed", client =>
{
    client.BaseAddress = origin;
    client.Timeout = TimeSpan.FromSeconds(5);
    client.DefaultRequestHeaders.Add("X-API-Key", key);
}).ConfigurePrimaryHttpMessageHandler(() => new HttpClientHandler { AllowAutoRedirect = false });

var app = builder.Build();
app.MapGet("/quote", async (string symbol, HttpContext context, IHttpClientFactory clients, CancellationToken cancellation) =>
{
    if (!Regex.IsMatch(symbol, @"\A(NASDAQ|NYSE|AMEX):[A-Z0-9._&!-]{1,48}\z"))
        return Results.BadRequest(new { error = "Use an exchange-qualified US symbol." });

    var path = QueryHelpers.AddQueryString("/v1/quotes", new Dictionary<string, string?> {
        ["market"] = "US", ["symbols"] = symbol
    });
    try
    {
        using var reply = await clients.CreateClient("zafeed").GetAsync(path, cancellation);
        if (reply.StatusCode == HttpStatusCode.TooManyRequests)
        {
            var retry = reply.Headers.RetryAfter;
            var delay = retry?.Delta ?? (retry?.Date - DateTimeOffset.UtcNow) ?? TimeSpan.FromSeconds(1);
            context.Response.Headers["Retry-After"] = Math.Max(0, Math.Ceiling(delay.TotalSeconds))
                .ToString(CultureInfo.InvariantCulture);
            context.Response.Headers["Cache-Control"] = "no-store";
            return Results.Json(new { error = "Quote rate limit reached. Retry after the indicated delay." }, statusCode: 429);
        }
        if (!reply.IsSuccessStatusCode)
            return Results.Json(new { error = "Quote request failed", upstreamStatus = (int)reply.StatusCode }, statusCode: 502);

        return Results.Content(await reply.Content.ReadAsStringAsync(cancellation), "application/json");
    }
    catch (OperationCanceledException) when (!cancellation.IsCancellationRequested)
    {
        return Results.Json(new { error = "Quote request timed out." }, statusCode: 504);
    }
    catch (HttpRequestException)
    {
        return Results.Json(new { error = "Quote service unavailable." }, statusCode: 502);
    }
});

app.Run();
