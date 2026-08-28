using LabLink.Api.Domain.Enums;
using LabLink.Api.Domain.Models;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;
using LabLink.Api.Repositories;

namespace LabLink.Api.Services;

public class TestResultService
{
    private readonly ITestResultRepository _testResultRepository;
    private readonly ITestRunRepository _testRunRepository;
    private readonly ILogger<TestResultService> _logger;

    public TestResultService(
        ITestResultRepository testResultRepository,
        ITestRunRepository testRunRepository,
        ILogger<TestResultService> logger
    )
    {
        _testResultRepository = testResultRepository;
        _testRunRepository = testRunRepository;
        _logger = logger;
    }

    public async Task<IEnumerable<TestResultResponse>> GetResultsByRunIdAsync(string testRunId)
    {
        var run = await _testRunRepository.GetByIdAsync(testRunId);
        if (run == null)
        {
            throw new EntityNotFoundException(nameof(TestRun), testRunId);
        }

        var results = await _testResultRepository.GetByTestRunIdAsync(testRunId);
        return results.Select(ToResponse);
    }

    public async Task<TestResultResponse> IngestResultAsync(string testRunId, CreateTestResultRequest request)
    {
        var run = await _testRunRepository.GetByIdAsync(testRunId);
        if (run == null)
        {
            throw new EntityNotFoundException(nameof(TestRun), testRunId);
        }

        if (run.Status == TestRunStatus.Completed || run.Status == TestRunStatus.Cancelled)
        {
            throw new InvalidStateTransitionException(
                run.Status.ToString(),
                "IngestResult (Run already finished)"
            );
        }

        if (string.IsNullOrWhiteSpace(request.TestName))
        {
            throw new ValidationException("Test name cannot be empty.");
        }

        if (request.Duration < 0.0)
        {
            throw new ValidationException("Test duration cannot be negative.");
        }

        // Transition run to Running status if currently Created
        if (run.Status == TestRunStatus.Created)
        {
            run.Status = TestRunStatus.Running;
            await _testRunRepository.UpdateAsync(run);
        }

        var result = new TestResult
        {
            TestRunId = testRunId,
            TestCaseId = request.TestCaseId ?? string.Empty,
            TestName = request.TestName.Trim(),
            Status = request.Status,
            Duration = request.Duration,
            ErrorMessage = request.ErrorMessage,
            Timestamp = DateTime.UtcNow
        };

        var created = await _testResultRepository.AddAsync(result);
        _logger.LogInformation(
            "Ingested test result '{TestName}' for run '{RunId}' -> Status: {Status}, Duration: {Duration}s",
            created.TestName,
            testRunId,
            created.Status,
            created.Duration
        );

        return ToResponse(created);
    }

    private static TestResultResponse ToResponse(TestResult r) =>
        new(
            r.Id,
            r.TestRunId,
            r.TestCaseId,
            r.TestName,
            r.Status.ToString(),
            r.Duration,
            r.ErrorMessage,
            r.Timestamp
        );
}
