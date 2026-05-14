using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Domain.Entities;

public class TestCase
{
    public Guid Id { get; set; }
    public Guid RequirementId { get; set; }
    public Requirement? Requirement { get; set; }
    public Guid? UserStoryId { get; set; }
    public UserStory? UserStory { get; set; }

    public string Title { get; set; } = string.Empty;
    public TestCaseKind Kind { get; set; } = TestCaseKind.Positive;
    public string Preconditions { get; set; } = string.Empty;

    /// <summary>JSON-encoded list of step strings.</summary>
    public string StepsJson { get; set; } = "[]";

    public string ExpectedResult { get; set; } = string.Empty;
    public int OrderIndex { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
