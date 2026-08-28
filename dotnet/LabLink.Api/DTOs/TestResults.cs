using System.ComponentModel.DataAnnotations;
using LabLink.Api.Domain.Enums;

namespace LabLink.Api.DTOs;

public record CreateTestResultRequest(
    [Required] string TestName,
    string? TestCaseId,
    [Required] TestStatus Status,
    [Range(0.0, double.MaxValue, ErrorMessage = "Duration must be non-negative.")] double Duration,
    string? ErrorMessage
);

public record TestResultResponse(
    string Id,
    string TestRunId,
    string TestCaseId,
    string TestName,
    string Status,
    double Duration,
    string? ErrorMessage,
    DateTime Timestamp
);
