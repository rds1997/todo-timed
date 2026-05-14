using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Domain.Entities;

public class ChatMessage
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid RequirementId { get; set; }
    public Requirement? Requirement { get; set; }

    public ChatRole Role { get; set; } = ChatRole.User;
    public string Content { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
