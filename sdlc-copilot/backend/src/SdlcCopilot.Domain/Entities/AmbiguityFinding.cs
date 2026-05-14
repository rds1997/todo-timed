using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Domain.Entities;

public class AmbiguityFinding
{
    public Guid Id { get; set; }
    public Guid RequirementId { get; set; }
    public Requirement? Requirement { get; set; }

    public string Excerpt { get; set; } = string.Empty;
    public string Issue { get; set; } = string.Empty;
    public string Suggestion { get; set; } = string.Empty;
    public Severity Severity { get; set; } = Severity.Medium;
    public string Category { get; set; } = "unclear"; // unclear | incomplete | conflicting | untestable
    public int OrderIndex { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
