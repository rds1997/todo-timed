using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using SdlcCopilot.Application.Abstractions;
using SdlcCopilot.Application.Ai;
using SdlcCopilot.Application.Services;
using SdlcCopilot.Infrastructure.Ai;
using SdlcCopilot.Infrastructure.Documents;
using SdlcCopilot.Infrastructure.Persistence;

namespace SdlcCopilot.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddSdlcInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("Default")
            ?? configuration["ConnectionStrings__Default"]
            ?? "Host=localhost;Port=5432;Database=sdlc_copilot;Username=sdlc;Password=sdlc";

        services.AddDbContext<AppDbContext>(opts => opts.UseNpgsql(connectionString));
        services.AddScoped<IRequirementRepository, RequirementRepository>();
        services.AddScoped<IDocumentTextExtractor, DocumentTextExtractor>();
        services.AddScoped<IRequirementService, RequirementService>();
        services.AddScoped<IChatService, ChatService>();

        var aiBaseUrl = configuration["AiService:BaseUrl"]
            ?? Environment.GetEnvironmentVariable("AI_SERVICE_BASE_URL")
            ?? "http://localhost:8001";
        services.AddHttpClient<IAiService, HttpAiService>(client =>
        {
            client.BaseAddress = new Uri(aiBaseUrl);
            client.Timeout = TimeSpan.FromSeconds(120);
        });

        return services;
    }
}
