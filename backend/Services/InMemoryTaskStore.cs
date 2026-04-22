using System.Collections.Concurrent;
using TodoApi.Models;

namespace TodoApi.Services;

public class InMemoryTaskStore : ITaskStore
{
    private readonly ConcurrentDictionary<Guid, TodoTask> _tasks = new();

    public IReadOnlyList<TodoTask> GetAll()
        => _tasks.Values.OrderBy(t => t.EndTime).ToList();

    public TodoTask? GetById(Guid id)
        => _tasks.TryGetValue(id, out var task) ? task : null;

    public TodoTask Add(TodoTask task)
    {
        task.Id = task.Id == Guid.Empty ? Guid.NewGuid() : task.Id;
        task.CreatedAt = DateTime.UtcNow;
        _tasks[task.Id] = task;
        return task;
    }

    public TodoTask? Update(Guid id, Action<TodoTask> mutator)
    {
        if (!_tasks.TryGetValue(id, out var existing))
        {
            return null;
        }
        lock (existing)
        {
            mutator(existing);
        }
        return existing;
    }

    public bool Delete(Guid id) => _tasks.TryRemove(id, out _);
}
