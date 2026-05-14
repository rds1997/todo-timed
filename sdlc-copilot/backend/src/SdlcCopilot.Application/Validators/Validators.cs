using FluentValidation;
using SdlcCopilot.Application.Dtos;

namespace SdlcCopilot.Application.Validators;

public class IngestRequirementRequestValidator : AbstractValidator<IngestRequirementRequest>
{
    public IngestRequirementRequestValidator()
    {
        RuleFor(x => x.Title).NotEmpty().MaximumLength(200);
        RuleFor(x => x.Text).NotEmpty().MinimumLength(20)
            .WithMessage("Requirement text must contain at least 20 characters.");
    }
}

public class UpdateUserStoryRequestValidator : AbstractValidator<UpdateUserStoryRequest>
{
    public UpdateUserStoryRequestValidator()
    {
        RuleFor(x => x.Title).NotEmpty().MaximumLength(200);
        RuleFor(x => x.StoryPoints).GreaterThanOrEqualTo(0).LessThanOrEqualTo(100);
        RuleFor(x => x.EstimatedHours).GreaterThanOrEqualTo(0);
    }
}

public class UpdateTaskRequestValidator : AbstractValidator<UpdateTaskRequest>
{
    public UpdateTaskRequestValidator()
    {
        RuleFor(x => x.Title).NotEmpty().MaximumLength(200);
        RuleFor(x => x.Layer).NotEmpty();
        RuleFor(x => x.EstimatedHours).GreaterThanOrEqualTo(0);
    }
}

public class UpdateTestCaseRequestValidator : AbstractValidator<UpdateTestCaseRequest>
{
    public UpdateTestCaseRequestValidator()
    {
        RuleFor(x => x.Title).NotEmpty().MaximumLength(200);
        RuleFor(x => x.ExpectedResult).NotEmpty();
    }
}

public class ChatRequestValidator : AbstractValidator<ChatRequest>
{
    public ChatRequestValidator()
    {
        RuleFor(x => x.Message).NotEmpty().MaximumLength(2000);
    }
}
