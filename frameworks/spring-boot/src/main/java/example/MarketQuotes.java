package example;

import java.net.URI;
import java.net.http.HttpClient;
import java.time.Duration;
import java.util.Map;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

@SpringBootApplication
@RestController
public class MarketQuotes {
    private final RestClient upstream;
    private final Map<String, String> keys = Map.of(
        "US", required("ZAFEED_US_KEY"),
        "HK", required("ZAFEED_HK_KEY")
    );

    public MarketQuotes() {
        URI origin = URI.create(required("ZAFEED_BASE_URL"));
        boolean localDemo = "http".equals(origin.getScheme()) && "127.0.0.1".equals(origin.getHost());
        if (origin.getHost() == null || origin.getUserInfo() != null || origin.getQuery() != null ||
            origin.getFragment() != null || !origin.getPath().matches("/?") ||
            (!"https".equals(origin.getScheme()) && !localDemo)) {
            throw new IllegalArgumentException("Set ZAFEED_BASE_URL to an HTTPS origin or the loopback demo.");
        }
        var http = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(3))
            .followRedirects(HttpClient.Redirect.NEVER).build();
        var requests = new JdkClientHttpRequestFactory(http);
        requests.setReadTimeout(Duration.ofSeconds(5));
        upstream = RestClient.builder().baseUrl(origin.toString()).requestFactory(requests).build();
    }

    @GetMapping("/quotes/{market}")
    ResponseEntity<?> quote(@PathVariable String market, @RequestParam String symbol) {
        String key = keys.get(market);
        boolean validVenue = switch (market) {
            case "US" -> symbol.matches("(NASDAQ|NYSE|AMEX):[A-Z0-9._&!-]{1,48}");
            case "HK" -> symbol.matches("HKEX:[0-9]{5}");
            default -> false;
        };
        if (key == null || !validVenue) {
            return ResponseEntity.badRequest().body(Map.of("error", "Choose US or HK and a matching symbol."));
        }
        try {
            String body = upstream.get()
                .uri("/v1/quotes?market={market}&symbols={symbol}", market, symbol)
                .header("X-API-Key", key)
                .retrieve().onStatus(status -> !status.is2xxSuccessful(), (request, response) -> {
                    throw new RestClientResponseException("Quote request failed", response.getStatusCode().value(),
                        "", null, null, null);
                }).body(String.class);
            return ResponseEntity.ok().contentType(MediaType.APPLICATION_JSON).body(body);
        } catch (RestClientResponseException error) {
            return ResponseEntity.status(502).body(Map.of("error", "Quote request failed", "upstreamStatus", error.getStatusCode().value()));
        } catch (RestClientException error) {
            return ResponseEntity.status(502).body(Map.of("error", "Quote service unavailable"));
        }
    }

    private static String required(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) throw new IllegalStateException("Set " + name);
        return value;
    }

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(MarketQuotes.class);
        app.setDefaultProperties(Map.of("server.address", "127.0.0.1", "server.port", "8104"));
        app.run(args);
    }
}
