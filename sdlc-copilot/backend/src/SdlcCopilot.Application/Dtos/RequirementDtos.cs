using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Application.Dtos;

public record IngestRequirementRequest(string Title, string Text);

public record RequirementSummaryDto(
    Guid Id,
    string Title,
    string? SourceFileName,
    RequirementStatus Status,
    DateTime CreatedAt,
    DateTime UpdatedAt,
    int UserStoryCount,
    int TaskCount,
    int TestCaseCount,
    int AmbiguityCount);

public record RequirementDetailDto(
    Guid Id,
    string Title,
    string SourceText,
    string? SourceFileName,
    RequirementStatus Status,
    DateTime CreatedAt,
    DateTime UpdatedAt,
    AnalysisDto? Analysis,
    IReadOnlyList<EpicDto> Epics,
    IReadOnlyList<UserStoryDto> UserStories,
    IReadOnlyList<DevTaskDto> Tasks,
    IReadOnlyList<TestCaseDto> TestCases,
    IReadOnlyList<AmbiguityFindingDto> Ambiguities,
    EstimationSummaryDto Estimation);

public record AnalysisDto(
    string Summary,
    string Goals,
    string Stakeholders,
    string KeyConstraints);

public record EpicDto(
    Guid Id,
    string Title,
    string Description,
    int OrderIndex);

public record UserStoryDto(
    Guid Id,
    Guid? EpicId,
    string Title,
    string AsA,
    string IWant,
    string SoThat,
    IReadOnlyList<string> AcceptanceCriteria,
    int StoryPoints,
    Complexity Complexity,
    decimal EstimatedHours,
    int OrderIndex);

public record DevTaskDto(
    Guid Id,
    Guid? UserStoryId,
    string Title,
    string Description,
    string Layer,
    decimal EstimatedHours,
    Complexity Complexity,
    int OrderIndex);

public record TestCaseDto(
    Guid Id,
    Guid? UserStoryId,
    string Title,
    TestCaseKind Kind,
    string Preconditions,
    IReadOnlyList<string> Steps,
    string ExpectedResult,
    int OrderIndex);

public record AmbiguityFindingDto(
    Guid Id,
    string Excerpt,
    string Issue,
    string Suggestion,
    Severity Severity,
    string Category,
    int OrderIndex);

public record EstimationSummaryDto(
    int TotalStoryPoints,
    decimal TotalEstimatedHours,
    decimal BackendHours,
    decimal FrontendHours,
    decimal QaHours,
    decimal InfraHours,
    int StoryCount,
    int TaskCount);

public record UpdateUserStoryRequest(
    string Title,
    string AsA,
    string IWant,
    string SoThat,
    IReadOnlyList<string> AcceptanceCriteria,
    int StoryPoints,
    Complexity Complexity,
    decimal EstimatedHours);

public record UpdateTaskRequest(
    string Title,
    string Description,
    string Layer,
    decimal EstimatedHours,
    Complexity Complexity);

public record UpdateTestCaseRequest(
    string Title,
    TestCaseKind Kind,
    string Preconditions,
    IReadOnlyList<string> Steps,
    string ExpectedResult);
