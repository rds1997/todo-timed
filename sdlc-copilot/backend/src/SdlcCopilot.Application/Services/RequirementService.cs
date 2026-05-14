using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using SdlcCopilot.Application.Abstractions;
using SdlcCopilot.Application.Ai;
using SdlcCopilot.Application.Common;
using SdlcCopilot.Application.Dtos;
using SdlcCopilot.Application.Mapping;
using SdlcCopilot.Domain.Entities;
using SdlcCopilot.Domain.Enums;

namespace SdlcCopilot.Application.Services;

public class RequirementService : IRequirementService
{
    private readonly IRequirementRepository _repo;
    private readonly IAiService _ai;
    private readonly IDocumentTextExtractor _extractor;
    private readonly ILogger<RequirementService> _logger;

    public RequirementService(
        IRequirementRepository repo,
        IAiService ai,
        IDocumentTextExtractor extractor,
        ILogger<RequirementService> logger)
    {
        _repo = repo;
        _ai = ai;
        _extractor = extractor;
        _logger = logger;
    }

    public async Task<RequirementSummaryDto> IngestTextAsync(IngestRequirementRequest request, CancellationToken cancellationToken = default)
    {
        var entity = new Requirement
        {
            Title = string.IsNullOrWhiteSpace(request.Title) ? "Untitled requirement" : request.Title.Trim(),
            SourceText = request.Text?.Trim() ?? string.Empty,
            Status = RequirementStatus.Ingested
        };
        await _repo.AddAsync(entity, cancellationToken);
        await _repo.SaveChangesAsync(cancellationToken);
        _logger.LogInformation("Ingested requirement {Id} ({Length} chars)", entity.Id, entity.SourceText.Length);
        return Mapper.ToSummaryDto(entity);
    }

    public async Task<RequirementSummaryDto> IngestFileAsync(string title, Stream content, string fileName, string? contentType, CancellationToken cancellationToken = default)
    {
        var text = await _extractor.ExtractAsync(content, fileName, contentType, cancellationToken);
        var entity = new Requirement
        {
            Title = string.IsNullOrWhiteSpace(title) ? Path.GetFileNameWithoutExtension(fileName) : title.Trim(),
            SourceText = text,
            SourceFileName = fileName,
            Status = RequirementStatus.Ingested
        };
        await _repo.AddAsync(entity, cancellationToken);
        await _repo.SaveChangesAsync(cancellationToken);
        _logger.LogInformation("Ingested requirement file {Id} {FileName} ({Length} chars)", entity.Id, fileName, text.Length);
        return Mapper.ToSummaryDto(entity);
    }

    public async Task<IReadOnlyList<RequirementSummaryDto>> ListAsync(CancellationToken cancellationToken = default)
    {
        var items = await _repo.ListAsync(cancellationToken);
        return items.Select(Mapper.ToSummaryDto).ToList();
    }

    public async Task<Result<RequirementDetailDto>> GetAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var entity = await _repo.GetWithChildrenAsync(id, tracking: false, cancellationToken);
        if (entity is null) return Result<RequirementDetailDto>.NotFound();
        return Result<RequirementDetailDto>.Success(Mapper.ToDetailDto(entity));
    }

    public async Task<Result<RequirementDetailDto>> AnalyzeAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var entity = await _repo.GetWithChildrenAsync(id, tracking: true, cancellationToken);
        if (entity is null) return Result<RequirementDetailDto>.NotFound();

        entity.Status = RequirementStatus.Analyzing;
        entity.UpdatedAt = DateTime.UtcNow;
        await _repo.SaveChangesAsync(cancellationToken);

        AiAnalyzeResponse aiResponse;
        try
        {
            aiResponse = await _ai.AnalyzeAsync(new AiAnalyzeRequest(entity.Title, entity.SourceText), cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "AI analyze failed for requirement {Id}", id);
            entity.Status = RequirementStatus.Failed;
            entity.UpdatedAt = DateTime.UtcNow;
            await _repo.SaveChangesAsync(cancellationToken);
            return Result<RequirementDetailDto>.Failure("AI analysis failed: " + ex.Message, 502);
        }

        ApplyAiResponse(entity, aiResponse);
        entity.Status = RequirementStatus.Analyzed;
        entity.UpdatedAt = DateTime.UtcNow;
        await _repo.SaveChangesAsync(cancellationToken);

        var refreshed = await _repo.GetWithChildrenAsync(id, tracking: false, cancellationToken);
        return Result<RequirementDetailDto>.Success(Mapper.ToDetailDto(refreshed!));
    }

    public async Task<Result<bool>> DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var entity = await _repo.GetByIdAsync(id, tracking: false, cancellationToken);
        if (entity is null) return Result<bool>.NotFound();
        await _repo.DeleteAsync(id, cancellationToken);
        await _repo.SaveChangesAsync(cancellationToken);
        return Result<bool>.Success(true);
    }

    public async Task<Result<UserStoryDto>> UpdateUserStoryAsync(Guid requirementId, Guid storyId, UpdateUserStoryRequest request, CancellationToken cancellationToken = default)
    {
        var story = await _repo.GetUserStoryAsync(storyId, cancellationToken);
        if (story is null || story.RequirementId != requirementId) return Result<UserStoryDto>.NotFound();
        story.Title = request.Title;
        story.AsA = request.AsA;
        story.IWant = request.IWant;
        story.SoThat = request.SoThat;
        story.AcceptanceCriteriaJson = Mapper.SerializeStrings(request.AcceptanceCriteria);
        story.StoryPoints = request.StoryPoints;
        story.Complexity = request.Complexity;
        story.EstimatedHours = request.EstimatedHours;
        await _repo.SaveChangesAsync(cancellationToken);
        return Result<UserStoryDto>.Success(Mapper.ToDto(story));
    }

    public async Task<Result<DevTaskDto>> UpdateTaskAsync(Guid requirementId, Guid taskId, UpdateTaskRequest request, CancellationToken cancellationToken = default)
    {
        var task = await _repo.GetTaskAsync(taskId, cancellationToken);
        if (task is null || task.RequirementId != requirementId) return Result<DevTaskDto>.NotFound();
        task.Title = request.Title;
        task.Description = request.Description;
        task.Layer = request.Layer;
        task.EstimatedHours = request.EstimatedHours;
        task.Complexity = request.Complexity;
        await _repo.SaveChangesAsync(cancellationToken);
        return Result<DevTaskDto>.Success(Mapper.ToDto(task));
    }

    public async Task<Result<TestCaseDto>> UpdateTestCaseAsync(Guid requirementId, Guid testCaseId, UpdateTestCaseRequest request, CancellationToken cancellationToken = default)
    {
        var tc = await _repo.GetTestCaseAsync(testCaseId, cancellationToken);
        if (tc is null || tc.RequirementId != requirementId) return Result<TestCaseDto>.NotFound();
        tc.Title = request.Title;
        tc.Kind = request.Kind;
        tc.Preconditions = request.Preconditions;
        tc.StepsJson = Mapper.SerializeStrings(request.Steps);
        tc.ExpectedResult = request.ExpectedResult;
        await _repo.SaveChangesAsync(cancellationToken);
        return Result<TestCaseDto>.Success(Mapper.ToDto(tc));
    }

    public async Task<Result<string>> ExportMarkdownAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var entity = await _repo.GetWithChildrenAsync(id, tracking: false, cancellationToken);
        if (entity is null) return Result<string>.NotFound();
        var dto = Mapper.ToDetailDto(entity);
        var sb = new StringBuilder();
        sb.AppendLine($"# {dto.Title}");
        sb.AppendLine();
        if (dto.Analysis is not null)
        {
            sb.AppendLine("## Summary").AppendLine().AppendLine(dto.Analysis.Summary).AppendLine();
            sb.AppendLine("## Goals").AppendLine().AppendLine(dto.Analysis.Goals).AppendLine();
            sb.AppendLine("## Stakeholders").AppendLine().AppendLine(dto.Analysis.Stakeholders).AppendLine();
            sb.AppendLine("## Key Constraints").AppendLine().AppendLine(dto.Analysis.KeyConstraints).AppendLine();
        }
        if (dto.Epics.Any())
        {
            sb.AppendLine("## Epics").AppendLine();
            foreach (var e in dto.Epics) sb.AppendLine($"- **{e.Title}** — {e.Description}");
            sb.AppendLine();
        }
        if (dto.UserStories.Any())
        {
            sb.AppendLine("## User Stories").AppendLine();
            foreach (var s in dto.UserStories)
            {
                sb.AppendLine($"### {s.Title} _(SP {s.StoryPoints}, {s.Complexity}, {s.EstimatedHours}h)_");
                sb.AppendLine($"As a {s.AsA}, I want {s.IWant}, so that {s.SoThat}.");
                sb.AppendLine();
                sb.AppendLine("**Acceptance Criteria:**");
                foreach (var ac in s.AcceptanceCriteria) sb.AppendLine($"- {ac}");
                sb.AppendLine();
            }
        }
        if (dto.Tasks.Any())
        {
            sb.AppendLine("## Development Tasks").AppendLine();
            foreach (var t in dto.Tasks)
                sb.AppendLine($"- [{t.Layer}] **{t.Title}** ({t.EstimatedHours}h, {t.Complexity}) — {t.Description}");
            sb.AppendLine();
        }
        if (dto.TestCases.Any())
        {
            sb.AppendLine("## Test Cases").AppendLine();
            foreach (var t in dto.TestCases)
            {
                sb.AppendLine($"### [{t.Kind}] {t.Title}");
                if (!string.IsNullOrWhiteSpace(t.Preconditions)) sb.AppendLine($"**Preconditions:** {t.Preconditions}");
                sb.AppendLine("**Steps:**");
                for (int i = 0; i < t.Steps.Count; i++) sb.AppendLine($"{i + 1}. {t.Steps[i]}");
                sb.AppendLine($"**Expected:** {t.ExpectedResult}").AppendLine();
            }
        }
        if (dto.Ambiguities.Any())
        {
            sb.AppendLine("## Ambiguities").AppendLine();
            foreach (var a in dto.Ambiguities)
                sb.AppendLine($"- [{a.Severity}] _{a.Excerpt}_ — {a.Issue}. **Suggestion:** {a.Suggestion}");
            sb.AppendLine();
        }
        sb.AppendLine("## Estimation").AppendLine();
        sb.AppendLine($"- Total story points: **{dto.Estimation.TotalStoryPoints}**");
        sb.AppendLine($"- Total estimated hours: **{dto.Estimation.TotalEstimatedHours}h**");
        sb.AppendLine($"- Backend: {dto.Estimation.BackendHours}h · Frontend: {dto.Estimation.FrontendHours}h · QA: {dto.Estimation.QaHours}h · Infra: {dto.Estimation.InfraHours}h");
        return Result<string>.Success(sb.ToString());
    }

    public async Task<Result<string>> ExportJsonAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var entity = await _repo.GetWithChildrenAsync(id, tracking: false, cancellationToken);
        if (entity is null) return Result<string>.NotFound();
        var dto = Mapper.ToDetailDto(entity);
        var json = JsonSerializer.Serialize(dto, new JsonSerializerOptions { WriteIndented = true });
        return Result<string>.Success(json);
    }

    private static void ApplyAiResponse(Requirement entity, AiAnalyzeResponse ai)
    {
        // Replace previous analysis & children
        entity.Analysis = new Analysis
        {
            RequirementId = entity.Id,
            Summary = ai.Summary.Summary,
            Goals = ai.Summary.Goals,
            Stakeholders = ai.Summary.Stakeholders,
            KeyConstraints = ai.Summary.KeyConstraints,
            RawJson = JsonSerializer.Serialize(ai)
        };

        entity.Epics.Clear();
        entity.UserStories.Clear();
        entity.Tasks.Clear();
        entity.TestCases.Clear();
        entity.Ambiguities.Clear();

        var epicLookup = new Dictionary<string, Epic>(StringComparer.OrdinalIgnoreCase);
        int order = 0;
        foreach (var e in ai.Epics ?? new())
        {
            var epic = new Epic
            {
                RequirementId = entity.Id,
                Title = e.Title,
                Description = e.Description,
                OrderIndex = order++
            };
            entity.Epics.Add(epic);
            if (!epicLookup.ContainsKey(e.Title)) epicLookup[e.Title] = epic;
        }

        var storyLookup = new Dictionary<string, UserStory>(StringComparer.OrdinalIgnoreCase);
        order = 0;
        foreach (var s in ai.UserStories ?? new())
        {
            var story = new UserStory
            {
                RequirementId = entity.Id,
                Title = s.Title,
                AsA = s.AsA,
                IWant = s.IWant,
                SoThat = s.SoThat,
                AcceptanceCriteriaJson = Mapper.SerializeStrings(s.AcceptanceCriteria ?? new()),
                StoryPoints = s.StoryPoints,
                Complexity = ParseComplexity(s.Complexity),
                EstimatedHours = s.EstimatedHours,
                OrderIndex = order++,
                Epic = !string.IsNullOrWhiteSpace(s.EpicTitle) && epicLookup.TryGetValue(s.EpicTitle, out var epic) ? epic : null
            };
            entity.UserStories.Add(story);
            if (!storyLookup.ContainsKey(s.Title)) storyLookup[s.Title] = story;
        }

        order = 0;
        foreach (var t in ai.Tasks ?? new())
        {
            var task = new DevTask
            {
                RequirementId = entity.Id,
                Title = t.Title,
                Description = t.Description,
                Layer = string.IsNullOrWhiteSpace(t.Layer) ? "backend" : t.Layer.ToLowerInvariant(),
                EstimatedHours = t.EstimatedHours,
                Complexity = ParseComplexity(t.Complexity),
                OrderIndex = order++,
                UserStory = !string.IsNullOrWhiteSpace(t.StoryTitle) && storyLookup.TryGetValue(t.StoryTitle, out var s) ? s : null
            };
            entity.Tasks.Add(task);
        }

        order = 0;
        foreach (var tc in ai.TestCases ?? new())
        {
            entity.TestCases.Add(new TestCase
            {
                RequirementId = entity.Id,
                Title = tc.Title,
                Kind = ParseTestKind(tc.Kind),
                Preconditions = tc.Preconditions,
                StepsJson = Mapper.SerializeStrings(tc.Steps ?? new()),
                ExpectedResult = tc.ExpectedResult,
                OrderIndex = order++,
                UserStory = !string.IsNullOrWhiteSpace(tc.StoryTitle) && storyLookup.TryGetValue(tc.StoryTitle, out var s) ? s : null
            });
        }

        order = 0;
        foreach (var a in ai.Ambiguities ?? new())
        {
            entity.Ambiguities.Add(new AmbiguityFinding
            {
                RequirementId = entity.Id,
                Excerpt = a.Excerpt,
                Issue = a.Issue,
                Suggestion = a.Suggestion,
                Severity = ParseSeverity(a.Severity),
                Category = string.IsNullOrWhiteSpace(a.Category) ? "unclear" : a.Category.ToLowerInvariant(),
                OrderIndex = order++
            });
        }
    }

    private static Complexity ParseComplexity(string? value) => value?.ToLowerInvariant() switch
    {
        "trivial" => Complexity.Trivial,
        "low" => Complexity.Low,
        "high" => Complexity.High,
        "very_high" or "veryhigh" or "very high" => Complexity.VeryHigh,
        _ => Complexity.Medium
    };

    private static Severity ParseSeverity(string? value) => value?.ToLowerInvariant() switch
    {
        "low" => Severity.Low,
        "high" => Severity.High,
        "critical" => Severity.Critical,
        _ => Severity.Medium
    };

    private static TestCaseKind ParseTestKind(string? value) => value?.ToLowerInvariant() switch
    {
        "negative" => TestCaseKind.Negative,
        "edge" => TestCaseKind.Edge,
        _ => TestCaseKind.Positive
    };
}
