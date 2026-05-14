using Microsoft.EntityFrameworkCore;
using SdlcCopilot.Domain.Entities;

namespace SdlcCopilot.Infrastructure.Persistence;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Requirement> Requirements => Set<Requirement>();
    public DbSet<Analysis> Analyses => Set<Analysis>();
    public DbSet<Epic> Epics => Set<Epic>();
    public DbSet<UserStory> UserStories => Set<UserStory>();
    public DbSet<DevTask> DevTasks => Set<DevTask>();
    public DbSet<TestCase> TestCases => Set<TestCase>();
    public DbSet<AmbiguityFinding> AmbiguityFindings => Set<AmbiguityFinding>();
    public DbSet<ChatMessage> ChatMessages => Set<ChatMessage>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        base.OnModelCreating(b);

        b.Entity<Requirement>(e =>
        {
            e.ToTable("requirements");
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(200).IsRequired();
            e.Property(x => x.SourceText).IsRequired();
            e.Property(x => x.SourceFileName).HasMaxLength(255);
            e.Property(x => x.Status).HasConversion<int>();
            e.HasMany(x => x.Epics).WithOne(x => x.Requirement!).HasForeignKey(x => x.RequirementId).OnDelete(DeleteBehavior.Cascade);
            e.HasMany(x => x.UserStories).WithOne(x => x.Requirement!).HasForeignKey(x => x.RequirementId).OnDelete(DeleteBehavior.Cascade);
            e.HasMany(x => x.Tasks).WithOne(x => x.Requirement!).HasForeignKey(x => x.RequirementId).OnDelete(DeleteBehavior.Cascade);
            e.HasMany(x => x.TestCases).WithOne(x => x.Requirement!).HasForeignKey(x => x.RequirementId).OnDelete(DeleteBehavior.Cascade);
            e.HasMany(x => x.Ambiguities).WithOne(x => x.Requirement!).HasForeignKey(x => x.RequirementId).OnDelete(DeleteBehavior.Cascade);
            e.HasMany(x => x.ChatMessages).WithOne(x => x.Requirement!).HasForeignKey(x => x.RequirementId).OnDelete(DeleteBehavior.Cascade);
            e.HasOne(x => x.Analysis).WithOne(x => x.Requirement!).HasForeignKey<Analysis>(x => x.RequirementId).OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<Analysis>(e =>
        {
            e.ToTable("analyses");
            e.HasKey(x => x.Id);
            e.Property(x => x.RawJson).HasColumnType("jsonb");
        });

        b.Entity<Epic>(e =>
        {
            e.ToTable("epics");
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(200).IsRequired();
            e.HasMany(x => x.UserStories).WithOne(x => x.Epic!).HasForeignKey(x => x.EpicId).OnDelete(DeleteBehavior.SetNull);
        });

        b.Entity<UserStory>(e =>
        {
            e.ToTable("user_stories");
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(200).IsRequired();
            e.Property(x => x.AcceptanceCriteriaJson).HasColumnType("jsonb");
            e.Property(x => x.Complexity).HasConversion<int>();
            e.Property(x => x.EstimatedHours).HasPrecision(10, 2);
        });

        b.Entity<DevTask>(e =>
        {
            e.ToTable("dev_tasks");
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(200).IsRequired();
            e.Property(x => x.Layer).HasMaxLength(40);
            e.Property(x => x.Complexity).HasConversion<int>();
            e.Property(x => x.EstimatedHours).HasPrecision(10, 2);
            e.HasOne(x => x.UserStory).WithMany().HasForeignKey(x => x.UserStoryId).OnDelete(DeleteBehavior.SetNull);
        });

        b.Entity<TestCase>(e =>
        {
            e.ToTable("test_cases");
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(200).IsRequired();
            e.Property(x => x.Kind).HasConversion<int>();
            e.Property(x => x.StepsJson).HasColumnType("jsonb");
            e.HasOne(x => x.UserStory).WithMany().HasForeignKey(x => x.UserStoryId).OnDelete(DeleteBehavior.SetNull);
        });

        b.Entity<AmbiguityFinding>(e =>
        {
            e.ToTable("ambiguities");
            e.HasKey(x => x.Id);
            e.Property(x => x.Severity).HasConversion<int>();
            e.Property(x => x.Category).HasMaxLength(40);
        });

        b.Entity<ChatMessage>(e =>
        {
            e.ToTable("chat_messages");
            e.HasKey(x => x.Id);
            e.Property(x => x.Role).HasConversion<int>();
        });
    }
}
