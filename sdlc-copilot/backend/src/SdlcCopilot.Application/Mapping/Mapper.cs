using System.Text.Json;
using SdlcCopilot.Application.Dtos;
using SdlcCopilot.Domain.Entities;

namespace SdlcCopilot.Application.Mapping;

/// <summary>
/// Hand-rolled mappers between EF entities and DTOs.
/// Kept here so neither Domain nor Infrastructure needs to know about DTOs.
/// </summary>
public static class Mapper
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public static RequirementSummaryDto ToSummaryDto(Requirement r) => new(
        r.Id, r.Title, r.SourceFileName, r.Status, r.CreatedAt, r.UpdatedAt,
        r.UserStories.Count, r.Tasks.Count, r.TestCases.Count, r.Ambiguities.Count);

    public static RequirementDetailDto ToDetailDto(Requirement r)
    {
        var stories = r.UserStories
            .OrderBy(s => s.OrderIndex)
            .Select(ToDto)
            .ToList();
        var tasks = r.Tasks
            .OrderBy(t => t.OrderIndex)
            .Select(ToDto)
            .ToList();
        var testCases = r.TestCases
            .OrderBy(t => t.OrderIndex)
            .Select(ToDto)
            .ToList();
        var ambiguities = r.Ambiguities
            .OrderBy(a => a.OrderIndex)
            .Select(ToDto)
            .ToList();
        var epics = r.Epics
            .OrderBy(e => e.OrderIndex)
            .Select(e => new EpicDto(e.Id, e.Title, e.Description, e.OrderIndex))
            .ToList();

        return new RequirementDetailDto(
            r.Id, r.Title, r.SourceText, r.SourceFileName, r.Status,
            r.CreatedAt, r.UpdatedAt,
            r.Analysis is null ? null : new AnalysisDto(
                r.Analysis.Summary, r.Analysis.Goals, r.Analysis.Stakeholders, r.Analysis.KeyConstraints),
            epics, stories, tasks, testCases, ambiguities,
            BuildEstimation(stories, tasks));
    }

    public static UserStoryDto ToDto(UserStory s)
    {
        var ac = DeserializeStrings(s.AcceptanceCriteriaJson);
        return new UserStoryDto(s.Id, s.EpicId, s.Title, s.AsA, s.IWant, s.SoThat, ac,
            s.StoryPoints, s.Complexity, s.EstimatedHours, s.OrderIndex);
    }

    public static DevTaskDto ToDto(DevTask t) => new(
        t.Id, t.UserStoryId, t.Title, t.Description, t.Layer, t.EstimatedHours, t.Complexity, t.OrderIndex);

    public static TestCaseDto ToDto(TestCase t)
    {
        var steps = DeserializeStrings(t.StepsJson);
        return new TestCaseDto(t.Id, t.UserStoryId, t.Title, t.Kind, t.Preconditions, steps, t.ExpectedResult, t.OrderIndex);
    }

    public static AmbiguityFindingDto ToDto(AmbiguityFinding a) => new(
        a.Id, a.Excerpt, a.Issue, a.Suggestion, a.Severity, a.Category, a.OrderIndex);

    public static EstimationSummaryDto BuildEstimation(IReadOnlyList<UserStoryDto> stories, IReadOnlyList<DevTaskDto> tasks)
    {
        var totalPoints = stories.Sum(s => s.StoryPoints);
        var totalHours = tasks.Sum(t => t.EstimatedHours);
        if (totalHours == 0)
        {
            totalHours = stories.Sum(s => s.EstimatedHours);
        }
        decimal HoursFor(string layer) => tasks.Where(t => t.Layer.Equals(layer, StringComparison.OrdinalIgnoreCase)).Sum(t => t.EstimatedHours);
        return new EstimationSummaryDto(
            totalPoints,
            decimal.Round(totalHours, 2),
            decimal.Round(HoursFor("backend"), 2),
            decimal.Round(HoursFor("frontend"), 2),
            decimal.Round(HoursFor("qa"), 2),
            decimal.Round(HoursFor("infra"), 2),
            stories.Count,
            tasks.Count);
    }

    public static List<string> DeserializeStrings(string json)
    {
        if (string.IsNullOrWhiteSpace(json)) return new List<string>();
        try
        {
            return JsonSerializer.Deserialize<List<string>>(json, JsonOptions) ?? new List<string>();
        }
        catch
        {
            return new List<string>();
        }
    }

    public static string SerializeStrings(IEnumerable<string> values) =>
        JsonSerializer.Serialize(values ?? Enumerable.Empty<string>());
}
