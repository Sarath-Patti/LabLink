namespace LabLink.Api.Domain.Enums;

/// <summary>
/// Lifecycle state classification for an automated test run execution.
/// </summary>
public enum TestRunStatus
{
    Created,
    Running,
    Completed,
    Cancelled
}
