using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using SdlcCopilot.Application.Ai;

namespace SdlcCopilot.Infrastructure.Ai;

public class HttpAiService : IAiService
{
    private readonly HttpClient _http;
    private readonly ILogger<HttpAiService> _logger;
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public HttpAiService(HttpClient http, ILogger<HttpAiService> logger)
    {
        _http = http;
        _logger = logger;
    }

    public async Task<AiAnalyzeResponse> AnalyzeAsync(AiAnalyzeRequest request, CancellationToken cancellationToken = default)
    {
        using var response = await _http.PostAsJsonAsync("/api/v1/analyze", request, JsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();
        var payload = await response.Content.ReadFromJsonAsync<AiAnalyzeResponse>(JsonOptions, cancellationToken);
        if (payload is null) throw new InvalidOperationException("AI service returned an empty analyze response.");
        return payload;
    }

    public async Task<AiChatResponse> ChatAsync(AiChatRequest request, CancellationToken cancellationToken = default)
    {
        using var response = await _http.PostAsJsonAsync("/api/v1/chat", request, JsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();
        var payload = await response.Content.ReadFromJsonAsync<AiChatResponse>(JsonOptions, cancellationToken);
        if (payload is null) throw new InvalidOperationException("AI service returned an empty chat response.");
        return payload;
    }

    public async Task<bool> HealthAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            using var response = await _http.GetAsync("/health", cancellationToken);
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "AI service health check failed");
            return false;
        }
    }
}
