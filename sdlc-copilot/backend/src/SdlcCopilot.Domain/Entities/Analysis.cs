namespace SdlcCopilot.Domain.Entities;

public class Analysis
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid RequirementId { get; set; }
    public Requirement? Requirement { get; set; }

    public string Summary { get; set; } = string.Empty;
    public string Goals { get; set; } = string.Empty;
    public string Stakeholders { get; set; } = string.Empty;
    public string KeyConstraints { get; set; } = string.Empty;
    public string RawJson { get; set; } = "{}";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
