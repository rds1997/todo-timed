using Microsoft.AspNetCore.Mvc;
using SdlcCopilot.Application.Common;
using SdlcCopilot.Application.Dtos;
using SdlcCopilot.Application.Services;

namespace SdlcCopilot.Api.Controllers;

[ApiController]
[Route("api/v1/requirements/{requirementId:guid}/chat")]
[Produces("application/json")]
public class ChatController : ControllerBase
{
    private readonly IChatService _chat;

    public ChatController(IChatService chat) { _chat = chat; }

    [HttpGet]
    public async Task<ActionResult<IReadOnlyList<ChatMessageDto>>> History(Guid requirementId, CancellationToken cancellationToken)
        => Map(await _chat.GetHistoryAsync(requirementId, cancellationToken));

    [HttpPost]
    public async Task<ActionResult<ChatTurnResponse>> Send(Guid requirementId, [FromBody] ChatRequest request, CancellationToken cancellationToken)
        => Map(await _chat.SendAsync(requirementId, request, cancellationToken));

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
