using SdlcCopilot.Domain.Entities;

namespace SdlcCopilot.Application.Abstractions;

public interface IRequirementRepository
{
    Task<Requirement> AddAsync(Requirement requirement, CancellationToken cancellationToken = default);
    Task<Requirement?> GetByIdAsync(Guid id, bool tracking = false, CancellationToken cancellationToken = default);
    Task<Requirement?> GetWithChildrenAsync(Guid id, bool tracking = false, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<Requirement>> ListAsync(CancellationToken cancellationToken = default);
    Task UpdateAsync(Requirement requirement, CancellationToken cancellationToken = default);
    Task DeleteAsync(Guid id, CancellationToken cancellationToken = default);

    Task<UserStory?> GetUserStoryAsync(Guid id, CancellationToken cancellationToken = default);
    Task<DevTask?> GetTaskAsync(Guid id, CancellationToken cancellationToken = default);
    Task<TestCase?> GetTestCaseAsync(Guid id, CancellationToken cancellationToken = default);

    Task SaveChangesAsync(CancellationToken cancellationToken = default);
}
