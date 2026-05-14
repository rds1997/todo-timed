using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Domain.Entities;

public class DevTask
{
    public Guid Id { get; set; }
    public Guid RequirementId { get; set; }
    public Requirement? Requirement { get; set; }
    public Guid? UserStoryId { get; set; }
    public UserStory? UserStory { get; set; }

    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Layer { get; set; } = "backend"; // backend | frontend | infra | qa | data
    public decimal EstimatedHours { get; set; }
    public Complexity Complexity { get; set; } = Complexity.Medium;
    public int OrderIndex { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
