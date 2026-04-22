using TodoApi.Models;

namespace TodoApi.Services;

public interface ITaskStore
{
    IReadOnlyList<TodoTask> GetAll();
    TodoTask? GetById(Guid id);
    TodoTask Add(TodoTask task);
    TodoTask? Update(Guid id, Action<TodoTask> mutator);
    bool Delete(Guid id);
}
