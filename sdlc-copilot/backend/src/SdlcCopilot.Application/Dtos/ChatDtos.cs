using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Application.Dtos;

public record ChatMessageDto(Guid Id, ChatRole Role, string Content, DateTime CreatedAt);

public record ChatRequest(string Message);

public record ChatTurnResponse(ChatMessageDto UserMessage, ChatMessageDto AssistantMessage);
