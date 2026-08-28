using LabLink.Api.Domain.Enums;

namespace LabLink.Api.Domain.Models;

public class ManufacturingRun
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string DutId { get; set; } = string.Empty;
    public string SerialNumber { get; set; } = string.Empty;
    public string StationId { get; set; } = string.Empty;
    public string SequenceName { get; set; } = string.Empty;
    public string SequenceVersion { get; set; } = string.Empty;
    public string SoftwareVersion { get; set; } = string.Empty;
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }
    public double DurationSeconds { get; set; }
    public TestRunStatus Verdict { get; set; } = TestRunStatus.Created;
    public bool FirstPass { get; set; } = true;
    public FailureCode FailureCode { get; set; } = FailureCode.NONE;
    public string? FailureSummary { get; set; }
}
