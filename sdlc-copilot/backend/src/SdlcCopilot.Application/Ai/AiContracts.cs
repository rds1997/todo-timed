using System.Text.Json.Serialization;

namespace SdlcCopilot.Application.Ai;

/// <summary>
/// Wire contracts for the FastAPI ai-service. These are intentionally
/// flat / JSON-friendly and decoupled from the EF entities.
/// </summary>

public record AiAnalyzeRequest(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("text")] string Text);

public record AiAnalyzeResponse(
    [property: JsonPropertyName("summary")] AiSummary Summary,
    [property: JsonPropertyName("epics")] List<AiEpic> Epics,
    [property: JsonPropertyName("user_stories")] List<AiUserStory> UserStories,
    [property: JsonPropertyName("tasks")] List<AiTask> Tasks,
    [property: JsonPropertyName("test_cases")] List<AiTestCase> TestCases,
    [property: JsonPropertyName("ambiguities")] List<AiAmbiguity> Ambiguities,
    [property: JsonPropertyName("estimation")] AiEstimation Estimation,
    [property: JsonPropertyName("mode")] string Mode);

public record AiSummary(
    [property: JsonPropertyName("summary")] string Summary,
    [property: JsonPropertyName("goals")] string Goals,
    [property: JsonPropertyName("stakeholders")] string Stakeholders,
    [property: JsonPropertyName("key_constraints")] string KeyConstraints);

public record AiEpic(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("description")] string Description);

public record AiUserStory(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("as_a")] string AsA,
    [property: JsonPropertyName("i_want")] string IWant,
    [property: JsonPropertyName("so_that")] string SoThat,
    [property: JsonPropertyName("acceptance_criteria")] List<string> AcceptanceCriteria,
    [property: JsonPropertyName("story_points")] int StoryPoints,
    [property: JsonPropertyName("complexity")] string Complexity,
    [property: JsonPropertyName("estimated_hours")] decimal EstimatedHours,
    [property: JsonPropertyName("epic_title")] string? EpicTitle);

public record AiTask(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("description")] string Description,
    [property: JsonPropertyName("layer")] string Layer,
    [property: JsonPropertyName("estimated_hours")] decimal EstimatedHours,
    [property: JsonPropertyName("complexity")] string Complexity,
    [property: JsonPropertyName("story_title")] string? StoryTitle);

public record AiTestCase(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("kind")] string Kind, // positive | negative | edge
    [property: JsonPropertyName("preconditions")] string Preconditions,
    [property: JsonPropertyName("steps")] List<string> Steps,
    [property: JsonPropertyName("expected_result")] string ExpectedResult,
    [property: JsonPropertyName("story_title")] string? StoryTitle);

public record AiAmbiguity(
    [property: JsonPropertyName("excerpt")] string Excerpt,
    [property: JsonPropertyName("issue")] string Issue,
    [property: JsonPropertyName("suggestion")] string Suggestion,
    [property: JsonPropertyName("severity")] string Severity,
    [property: JsonPropertyName("category")] string Category);

public record AiEstimation(
    [property: JsonPropertyName("total_story_points")] int TotalStoryPoints,
    [property: JsonPropertyName("total_estimated_hours")] decimal TotalEstimatedHours,
    [property: JsonPropertyName("breakdown")] Dictionary<string, decimal> Breakdown);

public record AiChatMessage(
    [property: JsonPropertyName("role")] string Role,
    [property: JsonPropertyName("content")] string Content);

public record AiChatRequest(
    [property: JsonPropertyName("title")] string Title,
    [property: JsonPropertyName("text")] string Text,
    [property: JsonPropertyName("history")] List<AiChatMessage> History,
    [property: JsonPropertyName("message")] string Message);

public record AiChatResponse(
    [property: JsonPropertyName("reply")] string Reply,
    [property: JsonPropertyName("mode")] string Mode);
