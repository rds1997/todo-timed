using Microsoft.AspNetCore.Mvc;
using TodoApi.Dtos;
using TodoApi.Models;
using TodoApi.Services;

namespace TodoApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TasksController : ControllerBase
{
    private readonly ITaskStore _store;

    public TasksController(ITaskStore store)
    {
        _store = store;
    }

    [HttpGet]
    public ActionResult<IEnumerable<TodoTask>> GetAll()
        => Ok(_store.GetAll());

    [HttpGet("{id:guid}")]
    public ActionResult<TodoTask> GetById(Guid id)
    {
        var task = _store.GetById(id);
        return task is null ? NotFound() : Ok(task);
    }

    [HttpPost]
    public ActionResult<TodoTask> Create([FromBody] CreateTaskDto dto)
    {
        var task = _store.Add(new TodoTask
        {
            Title = dto.Title.Trim(),
            Description = dto.Description ?? string.Empty,
            StartTime = dto.StartTime,
            EndTime = dto.EndTime,
            IsCompleted = false,
        });
        return CreatedAtAction(nameof(GetById), new { id = task.Id }, task);
    }

    [HttpPut("{id:guid}")]
    public ActionResult<TodoTask> Update(Guid id, [FromBody] UpdateTaskDto dto)
    {
        var updated = _store.Update(id, task =>
        {
            task.Title = dto.Title.Trim();
            task.Description = dto.Description ?? string.Empty;
            task.StartTime = dto.StartTime;
            task.EndTime = dto.EndTime;
            task.IsCompleted = dto.IsCompleted;
        });
        return updated is null ? NotFound() : Ok(updated);
    }

    [HttpDelete("{id:guid}")]
    public IActionResult Delete(Guid id)
        => _store.Delete(id) ? NoContent() : NotFound();
}
