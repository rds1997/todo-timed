namespace SdlcCopilot.Domain.Entities;

public class Epic
{
    public Guid Id { get; set; }
    public Guid RequirementId { get; set; }
    public Requirement? Requirement { get; set; }

    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public int OrderIndex { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<UserStory> UserStories { get; set; } = new List<UserStory>();
}
