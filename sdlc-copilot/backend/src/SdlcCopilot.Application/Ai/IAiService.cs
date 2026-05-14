namespace SdlcCopilot.Application.Ai;

/// <summary>Calls the external Python FastAPI ai-service.</summary>
public interface IAiService
{
    Task<AiAnalyzeResponse> AnalyzeAsync(AiAnalyzeRequest request, CancellationToken cancellationToken = default);
    Task<AiChatResponse> ChatAsync(AiChatRequest request, CancellationToken cancellationToken = default);
    Task<bool> HealthAsync(CancellationToken cancellationToken = default);
}
