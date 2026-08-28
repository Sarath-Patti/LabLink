using LabLink.Api.Domain.Enums;

namespace LabLink.Api.Domain.Models;

/// <summary>
/// Domain entity representing an individual test case result ingested from a test run execution.
/// </summary>
public class TestResult
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string TestRunId { get; set; } = string.Empty;
    public string TestCaseId { get; set; } = string.Empty;
    public string TestName { get; set; } = string.Empty;
    public TestStatus Status { get; set; } = TestStatus.Pending;
    public double Duration { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}
