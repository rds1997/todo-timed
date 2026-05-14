using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Domain.Entities;

public class UserStory
{
    public Guid Id { get; set; }
    public Guid RequirementId { get; set; }
    public Requirement? Requirement { get; set; }
    public Guid? EpicId { get; set; }
    public Epic? Epic { get; set; }

    public string Title { get; set; } = string.Empty;
    public string AsA { get; set; } = string.Empty;
    public string IWant { get; set; } = string.Empty;
    public string SoThat { get; set; } = string.Empty;

    /// <summary>JSON-encoded list of acceptance-criteria strings.</summary>
    public string AcceptanceCriteriaJson { get; set; } = "[]";

    public int StoryPoints { get; set; }
    public Complexity Complexity { get; set; } = Complexity.Medium;
    public decimal EstimatedHours { get; set; }
    public int OrderIndex { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
