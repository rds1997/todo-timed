using SdlcCopilot.Application.Common;
using SdlcCopilot.Application.Dtos;

namespace SdlcCopilot.Application.Services;

public interface IRequirementService
{
    Task<RequirementSummaryDto> IngestTextAsync(IngestRequirementRequest request, CancellationToken cancellationToken = default);
    Task<RequirementSummaryDto> IngestFileAsync(string title, Stream content, string fileName, string? contentType, CancellationToken cancellationToken = default);

    Task<IReadOnlyList<RequirementSummaryDto>> ListAsync(CancellationToken cancellationToken = default);
    Task<Result<RequirementDetailDto>> GetAsync(Guid id, CancellationToken cancellationToken = default);
    Task<Result<RequirementDetailDto>> AnalyzeAsync(Guid id, CancellationToken cancellationToken = default);
    Task<Result<bool>> DeleteAsync(Guid id, CancellationToken cancellationToken = default);

    Task<Result<UserStoryDto>> UpdateUserStoryAsync(Guid requirementId, Guid storyId, UpdateUserStoryRequest request, CancellationToken cancellationToken = default);
    Task<Result<DevTaskDto>> UpdateTaskAsync(Guid requirementId, Guid taskId, UpdateTaskRequest request, CancellationToken cancellationToken = default);
    Task<Result<TestCaseDto>> UpdateTestCaseAsync(Guid requirementId, Guid testCaseId, UpdateTestCaseRequest request, CancellationToken cancellationToken = default);

    Task<Result<string>> ExportMarkdownAsync(Guid id, CancellationToken cancellationToken = default);
    Task<Result<string>> ExportJsonAsync(Guid id, CancellationToken cancellationToken = default);
}
