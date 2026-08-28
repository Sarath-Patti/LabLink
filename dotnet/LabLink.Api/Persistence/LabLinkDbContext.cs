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

    // Manufacturing v1.0 DbSets
    public DbSet<Dut> Duts => Set<Dut>();
    public DbSet<ManufacturingRun> ManufacturingRuns => Set<ManufacturingRun>();
    public DbSet<MeasurementRecord> MeasurementRecords => Set<MeasurementRecord>();

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

        // Dut configuration (v1.0)
        modelBuilder.Entity<Dut>(b =>
        {
            b.HasKey(d => d.Id);
            b.Property(d => d.SerialNumber).IsRequired().HasMaxLength(128);
            b.Property(d => d.PartNumber).HasMaxLength(128);
            b.Property(d => d.HardwareRevision).HasMaxLength(64);
            b.Property(d => d.FirmwareVersion).HasMaxLength(64);
            b.Property(d => d.Status).HasConversion<string>().HasMaxLength(64);
            b.HasIndex(d => d.SerialNumber).IsUnique();
        });

        // ManufacturingRun configuration (v1.0)
        modelBuilder.Entity<ManufacturingRun>(b =>
        {
            b.HasKey(r => r.Id);
            b.Property(r => r.DutId).IsRequired().HasMaxLength(128);
            b.Property(r => r.SerialNumber).IsRequired().HasMaxLength(128);
            b.Property(r => r.StationId).HasMaxLength(128);
            b.Property(r => r.SequenceName).HasMaxLength(128);
            b.Property(r => r.SequenceVersion).HasMaxLength(64);
            b.Property(r => r.SoftwareVersion).HasMaxLength(64);
            b.Property(r => r.Verdict).HasConversion<string>().HasMaxLength(64);
            b.Property(r => r.FailureCode).HasConversion<string>().HasMaxLength(128);

            b.HasOne<Dut>()
                .WithMany()
                .HasForeignKey(r => r.DutId)
                .OnDelete(DeleteBehavior.Restrict);

            b.HasIndex(r => r.DutId);
            b.HasIndex(r => r.SerialNumber);
            b.HasIndex(r => r.StartedAt);
            b.HasIndex(r => r.Verdict);
        });

        // MeasurementRecord configuration (v1.0)
        modelBuilder.Entity<MeasurementRecord>(b =>
        {
            b.HasKey(m => m.Id);
            b.Property(m => m.ManufacturingRunId).IsRequired().HasMaxLength(128);
            b.Property(m => m.DutId).IsRequired().HasMaxLength(128);
            b.Property(m => m.StepName).IsRequired().HasMaxLength(128);
            b.Property(m => m.MeasurementName).IsRequired().HasMaxLength(128);
            b.Property(m => m.Unit).HasMaxLength(64);
            b.Property(m => m.ExpectedValue).HasMaxLength(128);
            b.Property(m => m.Verdict).HasConversion<string>().HasMaxLength(64);
            b.Property(m => m.FailureCode).HasConversion<string>().HasMaxLength(128);
            b.Property(m => m.InstrumentSource).HasMaxLength(128);

            b.HasOne<ManufacturingRun>()
                .WithMany()
                .HasForeignKey(m => m.ManufacturingRunId)
                .OnDelete(DeleteBehavior.Restrict);

            b.HasIndex(m => m.ManufacturingRunId);
            b.HasIndex(m => m.DutId);
            b.HasIndex(m => m.Timestamp);
        });
    }
}
