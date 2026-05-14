using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Domain.Entities;

public class Requirement
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Title { get; set; } = string.Empty;
    public string SourceText { get; set; } = string.Empty;
    public string? SourceFileName { get; set; }
    public RequirementStatus Status { get; set; } = RequirementStatus.Ingested;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public Analysis? Analysis { get; set; }
    public ICollection<Epic> Epics { get; set; } = new List<Epic>();
    public ICollection<UserStory> UserStories { get; set; } = new List<UserStory>();
    public ICollection<DevTask> Tasks { get; set; } = new List<DevTask>();
    public ICollection<TestCase> TestCases { get; set; } = new List<TestCase>();
    public ICollection<AmbiguityFinding> Ambiguities { get; set; } = new List<AmbiguityFinding>();
    public ICollection<ChatMessage> ChatMessages { get; set; } = new List<ChatMessage>();
}
