using System.Text;
using SdlcCopilot.Application.Abstractions;
using UglyToad.PdfPig;

namespace SdlcCopilot.Infrastructure.Documents;

public class DocumentTextExtractor : IDocumentTextExtractor
{
    public async Task<string> ExtractAsync(Stream content, string fileName, string? contentType, CancellationToken cancellationToken = default)
    {
        var ext = Path.GetExtension(fileName ?? string.Empty).ToLowerInvariant();
        if (ext == ".pdf" || contentType == "application/pdf")
        {
            using var ms = new MemoryStream();
            await content.CopyToAsync(ms, cancellationToken);
            ms.Position = 0;
            return ExtractFromPdf(ms);
        }

        // Treat everything else (.txt, .md, .doc, .docx, unknown) as utf-8 text best-effort.
        // .docx is technically a zip, but for hackathon scope we strip non-printable.
        using var reader = new StreamReader(content, Encoding.UTF8, detectEncodingFromByteOrderMarks: true, leaveOpen: false);
        var text = await reader.ReadToEndAsync(cancellationToken);
        return CleanText(text);
    }

    private static string ExtractFromPdf(Stream stream)
    {
        using var doc = PdfDocument.Open(stream);
        var sb = new StringBuilder();
        foreach (var page in doc.GetPages())
        {
            sb.AppendLine(page.Text);
        }
        return CleanText(sb.ToString());
    }

    private static string CleanText(string raw)
    {
        if (string.IsNullOrWhiteSpace(raw)) return string.Empty;
        var sb = new StringBuilder(raw.Length);
        foreach (var ch in raw)
        {
            if (ch == '\n' || ch == '\r' || ch == '\t' || !char.IsControl(ch))
                sb.Append(ch);
        }
        return sb.ToString().Trim();
    }
}
