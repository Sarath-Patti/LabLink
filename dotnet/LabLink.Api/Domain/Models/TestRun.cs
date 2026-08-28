using LabLink.Api.Domain.Enums;

namespace LabLink.Api.Domain.Models;

/// <summary>
/// Domain entity representing an automated test execution run session.
/// </summary>
public class TestRun
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public TestRunStatus Status { get; set; } = TestRunStatus.Created;
    public DateTime StartedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }
    public string Trigger { get; set; } = "Manual";
    public string Environment { get; set; } = "Development";
    public int TotalTests { get; set; }
    public int PassedTests { get; set; }
    public int FailedTests { get; set; }
    public int SkippedTests { get; set; }
}
