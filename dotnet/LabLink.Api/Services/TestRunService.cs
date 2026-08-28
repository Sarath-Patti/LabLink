using LabLink.Api.Domain.Enums;
using LabLink.Api.Domain.Models;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;
using LabLink.Api.Repositories;

namespace LabLink.Api.Services;

public class TestRunService
{
    private readonly ITestRunRepository _testRunRepository;
    private readonly ITestResultRepository _testResultRepository;
    private readonly ILogger<TestRunService> _logger;

    public TestRunService(
        ITestRunRepository testRunRepository,
        ITestResultRepository testResultRepository,
        ILogger<TestRunService> logger
    )
    {
        _testRunRepository = testRunRepository;
        _testResultRepository = testResultRepository;
        _logger = logger;
    }

    public async Task<IEnumerable<TestRunResponse>> GetAllAsync()
    {
        var runs = await _testRunRepository.GetAllAsync();
        return runs.Select(ToResponse);
    }

    public async Task<TestRunResponse> GetByIdAsync(string id)
    {
        var run = await _testRunRepository.GetByIdAsync(id);
        if (run == null)
        {
            throw new EntityNotFoundException(nameof(TestRun), id);
        }
        return ToResponse(run);
    }

    public async Task<TestRunResponse> CreateAsync(CreateTestRunRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Name))
        {
            throw new ValidationException("Test run name cannot be empty.");
        }

        var run = new TestRun
        {
            Name = request.Name.Trim(),
            Status = TestRunStatus.Created,
            StartedAt = DateTime.UtcNow,
            Trigger = string.IsNullOrWhiteSpace(request.Trigger) ? "Manual" : request.Trigger.Trim(),
            Environment = string.IsNullOrWhiteSpace(request.Environment) ? "Development" : request.Environment.Trim(),
            TotalTests = 0,
            PassedTests = 0,
            FailedTests = 0,
            SkippedTests = 0
        };

        var created = await _testRunRepository.AddAsync(run);
        _logger.LogInformation("Created new test run '{Name}' [ID: {Id}]", created.Name, created.Id);
        return ToResponse(created);
    }

    public async Task<TestRunResponse> CompleteRunAsync(string id, CompleteTestRunRequest request)
    {
        var run = await _testRunRepository.GetByIdAsync(id);
        if (run == null)
        {
            throw new EntityNotFoundException(nameof(TestRun), id);
        }

        var targetStatus = request.Status;
        if (targetStatus == TestRunStatus.Created || targetStatus == TestRunStatus.Running)
        {
            throw new InvalidStateTransitionException(run.Status.ToString(), targetStatus.ToString());
        }

        if (run.Status == TestRunStatus.Completed || run.Status == TestRunStatus.Cancelled)
        {
            throw new InvalidStateTransitionException(run.Status.ToString(), targetStatus.ToString());
        }

        // Aggregate statistics from individual ingested TestResults
        var results = (await _testResultRepository.GetByTestRunIdAsync(id)).ToList();

        run.Status = targetStatus;
        run.CompletedAt = DateTime.UtcNow;
        run.TotalTests = results.Count;
        run.PassedTests = results.Count(r => r.Status == TestStatus.Passed);
        run.FailedTests = results.Count(r => r.Status == TestStatus.Failed);
        run.SkippedTests = results.Count(r => r.Status == TestStatus.Skipped);

        var updated = await _testRunRepository.UpdateAsync(run);
        _logger.LogInformation(
            "Completed test run '{Name}' [ID: {Id}] -> Status: {Status}, Total: {Total}, Passed: {Passed}, Failed: {Failed}",
            updated.Name,
            updated.Id,
            updated.Status,
            updated.TotalTests,
            updated.PassedTests,
            updated.FailedTests
        );

        return ToResponse(updated);
    }

    public static TestRunResponse ToResponse(TestRun r) =>
        new(
            r.Id,
            r.Name,
            r.Status.ToString(),
            r.StartedAt,
            r.CompletedAt,
            r.Trigger,
            r.Environment,
            r.TotalTests,
            r.PassedTests,
            r.FailedTests,
            r.SkippedTests
        );
}
