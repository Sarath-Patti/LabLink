using System.Text.Json;
using LabLink.Api.Domain.Models;
using Microsoft.EntityFrameworkCore;

namespace LabLink.Api.Persistence;

public class LabLinkDbContext : DbContext
{
    public LabLinkDbContext(DbContextOptions<LabLinkDbContext> options) : base(options) { }

    public DbSet<TestCase> TestCases => Set<TestCase>();
    public DbSet<TestRun> TestRuns => Set<TestRun>();
    public DbSet<TestResult> TestResults => Set<TestResult>();
    public DbSet<Device> Devices => Set<Device>();
    public DbSet<Instrument> Instruments => Set<Instrument>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // TestCase configuration
        modelBuilder.Entity<TestCase>(b =>
        {
            b.HasKey(t => t.Id);
            b.Property(t => t.Name).IsRequired().HasMaxLength(256);
            b.Property(t => t.Suite).HasMaxLength(128);
            b.Property(t => t.Category).HasMaxLength(128);
            b.HasIndex(t => t.Name);
        });

        // TestRun configuration
        modelBuilder.Entity<TestRun>(b =>
        {
            b.HasKey(r => r.Id);
            b.Property(r => r.Name).IsRequired().HasMaxLength(256);
            b.Property(r => r.Status).HasConversion<string>().HasMaxLength(64);
            b.Property(r => r.Trigger).HasMaxLength(128);
            b.Property(r => r.Environment).HasMaxLength(128);
            b.HasIndex(r => r.StartedAt);
            b.HasIndex(r => r.Status);
        });

        // TestResult configuration
        modelBuilder.Entity<TestResult>(b =>
        {
            b.HasKey(r => r.Id);
            b.Property(r => r.TestName).IsRequired().HasMaxLength(256);
            b.Property(r => r.Status).HasConversion<string>().HasMaxLength(64);

            // Historical Protection: Do NOT cascade delete historical test results if a TestRun is deleted
            b.HasOne<TestRun>()
                .WithMany()
                .HasForeignKey(r => r.TestRunId)
                .OnDelete(DeleteBehavior.Restrict);

            b.HasOne<TestCase>()
                .WithMany()
                .HasForeignKey(r => r.TestCaseId)
                .IsRequired(false)
                .OnDelete(DeleteBehavior.SetNull);

            b.HasIndex(r => r.TestRunId);
            b.HasIndex(r => r.TestCaseId);
            b.HasIndex(r => r.Timestamp);
        });

        // Device configuration
        modelBuilder.Entity<Device>(b =>
        {
            b.HasKey(d => d.Id);
            b.Property(d => d.Name).IsRequired().HasMaxLength(256);
            b.Property(d => d.Type).HasConversion<string>().HasMaxLength(64);
            b.Property(d => d.Protocol).HasConversion<string>().HasMaxLength(64);
            b.Property(d => d.Address).HasMaxLength(256);

            // Store Metadata dictionary as JSON string
            b.Property(d => d.Metadata)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
                    v => JsonSerializer.Deserialize<Dictionary<string, string>>(v, (JsonSerializerOptions?)null) ?? new Dictionary<string, string>()
                );

            b.HasIndex(d => d.Name);
        });

        // Instrument configuration
        modelBuilder.Entity<Instrument>(b =>
        {
            b.HasKey(i => i.Id);
            b.Property(i => i.Name).IsRequired().HasMaxLength(256);
            b.Property(i => i.Type).HasMaxLength(128);
            b.Property(i => i.Interface).HasMaxLength(64);
            b.Property(i => i.Address).HasMaxLength(256);

            b.HasIndex(i => i.Name);
        });
    }
}
