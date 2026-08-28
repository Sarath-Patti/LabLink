namespace LabLink.Api.Domain.Enums;

/// <summary>
/// Status classification for an individual test result or measurement.
/// </summary>
public enum TestStatus
{
    Pending,
    Passed,
    Failed,
    Error,
    Skipped
}
