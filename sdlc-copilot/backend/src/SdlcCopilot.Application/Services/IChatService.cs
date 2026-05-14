using SdlcCopilot.Application.Common;
using SdlcCopilot.Application.Dtos;

namespace SdlcCopilot.Application.Services;

public interface IChatService
{
    Task<Result<IReadOnlyList<ChatMessageDto>>> GetHistoryAsync(Guid requirementId, CancellationToken cancellationToken = default);
    Task<Result<ChatTurnResponse>> SendAsync(Guid requirementId, ChatRequest request, CancellationToken cancellationToken = default);
}
