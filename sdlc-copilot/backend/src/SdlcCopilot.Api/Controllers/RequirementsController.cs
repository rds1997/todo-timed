using Microsoft.AspNetCore.Mvc;
using SdlcCopilot.Application.Common;
using SdlcCopilot.Application.Dtos;
using SdlcCopilot.Application.Services;

namespace SdlcCopilot.Api.Controllers;

[ApiController]
[Route("api/v1/requirements")]
[Produces("application/json")]
public class RequirementsController : ControllerBase
{
    private readonly IRequirementService _service;

    public RequirementsController(IRequirementService service)
    {
        _service = service;
    }

    /// <summary>List all ingested requirements.</summary>
    [HttpGet]
    [ProducesResponseType(typeof(IReadOnlyList<RequirementSummaryDto>), 200)]
    public async Task<ActionResult<IReadOnlyList<RequirementSummaryDto>>> List(CancellationToken cancellationToken)
        => Ok(await _service.ListAsync(cancellationToken));

    /// <summary>Get the full structured view of a requirement, including stories/tasks/tests/ambiguities.</summary>
    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(RequirementDetailDto), 200)]
    [ProducesResponseType(404)]
    public async Task<ActionResult<RequirementDetailDto>> Get(Guid id, CancellationToken cancellationToken)
    {
        var result = await _service.GetAsync(id, cancellationToken);
        return Map(result);
    }

    /// <summary>Ingest a raw text requirement.</summary>
    [HttpPost]
    [ProducesResponseType(typeof(RequirementSummaryDto), 201)]
    public async Task<ActionResult<RequirementSummaryDto>> Ingest([FromBody] IngestRequirementRequest request, CancellationToken cancellationToken)
    {
        var dto = await _service.IngestTextAsync(request, cancellationToken);
        return CreatedAtAction(nameof(Get), new { id = dto.Id }, dto);
    }

    /// <summary>Ingest a requirement from an uploaded file (txt, md, pdf, doc, docx).</summary>
    [HttpPost("upload")]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(RequirementSummaryDto), 201)]
    [RequestSizeLimit(20_000_000)]
    public async Task<ActionResult<RequirementSummaryDto>> Upload(
        [FromForm] IFormFile file,
        [FromForm] string? title,
        CancellationToken cancellationToken)
    {
        if (file is null || file.Length == 0) return BadRequest(new { error = "File is required." });
        await using var stream = file.OpenReadStream();
        var dto = await _service.IngestFileAsync(title ?? string.Empty, stream, file.FileName, file.ContentType, cancellationToken);
        return CreatedAtAction(nameof(Get), new { id = dto.Id }, dto);
    }

    /// <summary>Run AI analysis to generate stories, tasks, tests, ambiguity, and estimation.</summary>
    [HttpPost("{id:guid}/analyze")]
    [ProducesResponseType(typeof(RequirementDetailDto), 200)]
    [ProducesResponseType(404)]
    [ProducesResponseType(502)]
    public async Task<ActionResult<RequirementDetailDto>> Analyze(Guid id, CancellationToken cancellationToken)
        => Map(await _service.AnalyzeAsync(id, cancellationToken));

    [HttpDelete("{id:guid}")]
    [ProducesResponseType(204)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Delete(Guid id, CancellationToken cancellationToken)
    {
        var result = await _service.DeleteAsync(id, cancellationToken);
        if (!result.IsSuccess) return NotFound(new { error = result.Error });
        return NoContent();
    }

    [HttpPut("{id:guid}/user-stories/{storyId:guid}")]
    public async Task<ActionResult<UserStoryDto>> UpdateStory(Guid id, Guid storyId, [FromBody] UpdateUserStoryRequest request, CancellationToken cancellationToken)
        => Map(await _service.UpdateUserStoryAsync(id, storyId, request, cancellationToken));

    [HttpPut("{id:guid}/tasks/{taskId:guid}")]
    public async Task<ActionResult<DevTaskDto>> UpdateTask(Guid id, Guid taskId, [FromBody] UpdateTaskRequest request, CancellationToken cancellationToken)
        => Map(await _service.UpdateTaskAsync(id, taskId, request, cancellationToken));

    [HttpPut("{id:guid}/test-cases/{testCaseId:guid}")]
    public async Task<ActionResult<TestCaseDto>> UpdateTestCase(Guid id, Guid testCaseId, [FromBody] UpdateTestCaseRequest request, CancellationToken cancellationToken)
        => Map(await _service.UpdateTestCaseAsync(id, testCaseId, request, cancellationToken));

    [HttpGet("{id:guid}/export.md")]
    [Produces("text/markdown")]
    public async Task<IActionResult> ExportMarkdown(Guid id, CancellationToken cancellationToken)
    {
        var result = await _service.ExportMarkdownAsync(id, cancellationToken);
        if (!result.IsSuccess) return NotFound(new { error = result.Error });
        return File(System.Text.Encoding.UTF8.GetBytes(result.Value!), "text/markdown", $"requirement-{id}.md");
    }

    [HttpGet("{id:guid}/export.json")]
    public async Task<IActionResult> ExportJson(Guid id, CancellationToken cancellationToken)
    {
        var result = await _service.ExportJsonAsync(id, cancellationToken);
        if (!result.IsSuccess) return NotFound(new { error = result.Error });
        return File(System.Text.Encoding.UTF8.GetBytes(result.Value!), "application/json", $"requirement-{id}.json");
    }

    private ActionResult<T> Map<T>(Result<T> result)
    {
        if (result.IsSuccess) return Ok(result.Value);
        return result.StatusCode switch
        {
            404 => NotFound(new { error = result.Error }),
            502 => StatusCode(502, new { error = result.Error }),
            _ => BadRequest(new { error = result.Error }),
        };
    }
}
