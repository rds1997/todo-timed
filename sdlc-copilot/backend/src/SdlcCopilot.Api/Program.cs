using FluentValidation;
using FluentValidation.AspNetCore;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using SdlcCopilot.Api.Middleware;
using SdlcCopilot.Application.Validators;
using SdlcCopilot.Infrastructure;
using SdlcCopilot.Infrastructure.Persistence;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// --- Configuration: support PORT env (cloud) and standard env-vars ---
var port = Environment.GetEnvironmentVariable("PORT");
if (!string.IsNullOrEmpty(port))
{
    builder.WebHost.UseUrls($"http://0.0.0.0:{port}");
}

// --- Serilog: structured logging ---
builder.Host.UseSerilog((ctx, lc) => lc
    .ReadFrom.Configuration(ctx.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console());

// --- Services ---
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Intelligent SDLC Copilot API",
        Version = "v1",
        Description = "Converts raw software requirements into structured SDLC artifacts."
    });
});

builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddValidatorsFromAssemblyContaining<IngestRequirementRequestValidator>();

builder.Services.AddSdlcInfrastructure(builder.Configuration);

// --- CORS for the Angular frontend ---
var allowedOrigins = (builder.Configuration["Cors:AllowedOrigins"] ?? "http://localhost:4200")
    .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
builder.Services.AddCors(opts =>
{
    opts.AddDefaultPolicy(policy =>
    {
        if (allowedOrigins.Contains("*"))
        {
            policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader();
        }
        else
        {
            policy.WithOrigins(allowedOrigins).AllowAnyMethod().AllowAnyHeader();
        }
    });
});

// JWT-ready: configure authentication if a key is supplied via config (optional, off by default for hackathon demo).
// Auth services are wired but [Authorize] is not applied to controllers yet — flip on when ready.
var jwtAuthority = builder.Configuration["Jwt:Authority"];
if (!string.IsNullOrWhiteSpace(jwtAuthority))
{
    builder.Services.AddAuthentication("Bearer")
        .AddJwtBearer("Bearer", options =>
        {
            options.Authority = jwtAuthority;
            options.Audience = builder.Configuration["Jwt:Audience"];
            options.RequireHttpsMetadata = !builder.Environment.IsDevelopment();
        });
}
builder.Services.AddAuthorization();

var app = builder.Build();

// --- Middleware pipeline ---
app.UseSerilogRequestLogging();
app.UseMiddleware<ExceptionHandlingMiddleware>();

if (app.Environment.IsDevelopment() || builder.Configuration.GetValue<bool>("EnableSwagger"))
{
    app.UseSwagger();
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "SDLC Copilot API v1"));
}

app.UseCors();
app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/health", () => Results.Ok(new { status = "ok", service = "sdlc-copilot-api" }));
app.MapControllers();

// --- Auto-migrate on startup so docker-compose works out of the box ---
using (var scope = app.Services.CreateScope())
{
    try
    {
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        db.Database.Migrate();
    }
    catch (Exception ex)
    {
        var logger = scope.ServiceProvider.GetRequiredService<ILoggerFactory>().CreateLogger("Startup");
        logger.LogError(ex, "Database migration failed at startup. The API will still start, but requests will fail until DB is available.");
    }
}

app.Run();

public partial class Program { }
