using System.ComponentModel.DataAnnotations;
using LabLink.Api.Domain.Enums;

namespace LabLink.Api.DTOs;

public record CreateTestRunRequest(
    [Required] string Name,
    string Trigger = "Manual",
    string Environment = "Development"
);

public record CompleteTestRunRequest(
    TestRunStatus Status = TestRunStatus.Completed
);

public record TestRunResponse(
    string Id,
    string Name,
    string Status,
    DateTime StartedAt,
    DateTime? CompletedAt,
    string Trigger,
    string Environment,
    int TotalTests,
    int PassedTests,
    int FailedTests,
    int SkippedTests
);
