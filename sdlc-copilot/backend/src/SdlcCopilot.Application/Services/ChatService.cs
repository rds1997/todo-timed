using Microsoft.Extensions.Logging;
using SdlcCopilot.Application.Abstractions;
using SdlcCopilot.Application.Ai;
using SdlcCopilot.Application.Common;
using SdlcCopilot.Application.Dtos;
using SdlcCopilot.Domain.Entities;
using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Application.Services;

public class ChatService : IChatService
{
    private readonly IRequirementRepository _repo;
    private readonly IAiService _ai;
    private readonly ILogger<ChatService> _logger;

    public ChatService(IRequirementRepository repo, IAiService ai, ILogger<ChatService> logger)
    {
        _repo = repo;
        _ai = ai;
        _logger = logger;
    }

    public async Task<Result<IReadOnlyList<ChatMessageDto>>> GetHistoryAsync(Guid requirementId, CancellationToken cancellationToken = default)
    {
        var entity = await _repo.GetWithChildrenAsync(requirementId, tracking: false, cancellationToken);
        if (entity is null) return Result<IReadOnlyList<ChatMessageDto>>.NotFound();
        var dtos = entity.ChatMessages
            .OrderBy(m => m.CreatedAt)
            .Select(m => new ChatMessageDto(m.Id, m.Role, m.Content, m.CreatedAt))
            .ToList();
        return Result<IReadOnlyList<ChatMessageDto>>.Success(dtos);
    }

    public async Task<Result<ChatTurnResponse>> SendAsync(Guid requirementId, ChatRequest request, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(request.Message))
            return Result<ChatTurnResponse>.Failure("Message cannot be empty");

        var entity = await _repo.GetWithChildrenAsync(requirementId, tracking: true, cancellationToken);
        if (entity is null) return Result<ChatTurnResponse>.NotFound();

        var history = entity.ChatMessages
            .OrderBy(m => m.CreatedAt)
            .Select(m => new AiChatMessage(m.Role.ToString().ToLowerInvariant(), m.Content))
            .ToList();

        var userMsg = new ChatMessage
        {
            RequirementId = entity.Id,
            Role = ChatRole.User,
            Content = request.Message.Trim()
        };
        entity.ChatMessages.Add(userMsg);

        AiChatResponse aiResp;
        try
        {
            aiResp = await _ai.ChatAsync(new AiChatRequest(entity.Title, entity.SourceText, history, request.Message), cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "AI chat failed for requirement {Id}", requirementId);
            return Result<ChatTurnResponse>.Failure("AI chat failed: " + ex.Message, 502);
        }

        var assistantMsg = new ChatMessage
        {
            RequirementId = entity.Id,
            Role = ChatRole.Assistant,
            Content = aiResp.Reply
        };
        entity.ChatMessages.Add(assistantMsg);
        entity.UpdatedAt = DateTime.UtcNow;
        await _repo.SaveChangesAsync(cancellationToken);

        return Result<ChatTurnResponse>.Success(new ChatTurnResponse(
            new ChatMessageDto(userMsg.Id, userMsg.Role, userMsg.Content, userMsg.CreatedAt),
            new ChatMessageDto(assistantMsg.Id, assistantMsg.Role, assistantMsg.Content, assistantMsg.CreatedAt)));
    }
}
