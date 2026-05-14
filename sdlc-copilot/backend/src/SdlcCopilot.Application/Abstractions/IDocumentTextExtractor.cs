namespace SdlcCopilot.Application.Abstractions;

/// <summary>Extracts plain text from an uploaded file (txt, md, pdf, doc/docx).</summary>
public interface IDocumentTextExtractor
{
    Task<string> ExtractAsync(Stream content, string fileName, string? contentType, CancellationToken cancellationToken = default);
}
