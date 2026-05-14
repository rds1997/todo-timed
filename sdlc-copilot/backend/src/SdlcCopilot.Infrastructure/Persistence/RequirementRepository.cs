using Microsoft.EntityFrameworkCore;
using SdlcCopilot.Application.Abstractions;
using SdlcCopilot.Domain.Entities;

namespace SdlcCopilot.Infrastructure.Persistence;

public class RequirementRepository : IRequirementRepository
{
    private readonly AppDbContext _db;

    public RequirementRepository(AppDbContext db)
    {
        _db = db;
    }

    public async Task<Requirement> AddAsync(Requirement requirement, CancellationToken cancellationToken = default)
    {
        await _db.Requirements.AddAsync(requirement, cancellationToken);
        return requirement;
    }

    public async Task<Requirement?> GetByIdAsync(Guid id, bool tracking = false, CancellationToken cancellationToken = default)
    {
        var q = tracking ? _db.Requirements.AsQueryable() : _db.Requirements.AsNoTracking();
        return await q.FirstOrDefaultAsync(r => r.Id == id, cancellationToken);
    }

    public async Task<Requirement?> GetWithChildrenAsync(Guid id, bool tracking = false, CancellationToken cancellationToken = default)
    {
        IQueryable<Requirement> q = _db.Requirements
            .Include(r => r.Analysis)
            .Include(r => r.Epics)
            .Include(r => r.UserStories)
            .Include(r => r.Tasks)
            .Include(r => r.TestCases)
            .Include(r => r.Ambiguities)
            .Include(r => r.ChatMessages);
        if (!tracking) q = q.AsNoTracking();
        return await q.FirstOrDefaultAsync(r => r.Id == id, cancellationToken);
    }

    public async Task<IReadOnlyList<Requirement>> ListAsync(CancellationToken cancellationToken = default)
    {
        return await _db.Requirements
            .AsNoTracking()
            .Include(r => r.UserStories)
            .Include(r => r.Tasks)
            .Include(r => r.TestCases)
            .Include(r => r.Ambiguities)
            .OrderByDescending(r => r.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    public Task UpdateAsync(Requirement requirement, CancellationToken cancellationToken = default)
    {
        _db.Requirements.Update(requirement);
        return Task.CompletedTask;
    }

    public async Task DeleteAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var entity = await _db.Requirements.FirstOrDefaultAsync(r => r.Id == id, cancellationToken);
        if (entity is null) return;
        _db.Requirements.Remove(entity);
    }

    public Task<UserStory?> GetUserStoryAsync(Guid id, CancellationToken cancellationToken = default) =>
        _db.UserStories.FirstOrDefaultAsync(s => s.Id == id, cancellationToken);

    public Task<DevTask?> GetTaskAsync(Guid id, CancellationToken cancellationToken = default) =>
        _db.DevTasks.FirstOrDefaultAsync(t => t.Id == id, cancellationToken);

    public Task<TestCase?> GetTestCaseAsync(Guid id, CancellationToken cancellationToken = default) =>
        _db.TestCases.FirstOrDefaultAsync(t => t.Id == id, cancellationToken);

    public Task SaveChangesAsync(CancellationToken cancellationToken = default) =>
        _db.SaveChangesAsync(cancellationToken);
}
