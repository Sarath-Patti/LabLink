using System.Net;
using System.Net.Http.Json;
using LabLink.Api.Domain.Enums;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class TestResultApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public TestResultApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.UseSetting("Persistence:Provider", "InMemory");
        }).CreateClient();
    }

    [Fact]
    public async Task SubmitTestResult_ValidRequest_CalculatesMetricsCorrectly()
    {
        // 1. Create TestRun
        var runReq = new CreateTestRunRequest("result_ingestion_run", "UnitTests", "Development");
        var runRes = await _client.PostAsJsonAsync("/api/v1/test-runs", runReq);
        var run = await runRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(run);

        // 2. Submit Passed Result
        var passReq = new CreateTestResultRequest(
            TestName: "test_opm_power_measurement",
            TestCaseId: null,
            Status: TestStatus.Passed,
            Duration: 0.15,
            ErrorMessage: null
        );
        var passRes = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run.Id}/results", passReq);
        Assert.Equal(HttpStatusCode.Created, passRes.StatusCode);

        // 3. Submit Failed Result
        var failReq = new CreateTestResultRequest(
            TestName: "test_optical_switch_route_failure",
            TestCaseId: null,
            Status: TestStatus.Failed,
            Duration: 0.45,
            ErrorMessage: "Route hardware timeout"
        );
        var failRes = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run.Id}/results", failReq);
        Assert.Equal(HttpStatusCode.Created, failRes.StatusCode);

        // 4. Complete TestRun
        var completeRes = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run.Id}/complete", new CompleteTestRunRequest(TestRunStatus.Completed));
        Assert.Equal(HttpStatusCode.OK, completeRes.StatusCode);

        var completedRun = await completeRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(completedRun);
        Assert.Equal("Completed", completedRun.Status);
        Assert.Equal(2, completedRun.TotalTests);
        Assert.Equal(1, completedRun.PassedTests);
        Assert.Equal(1, completedRun.FailedTests);
        Assert.Equal(0, completedRun.SkippedTests);
    }

    [Fact]
    public async Task SubmitTestResult_InvalidDuration_ReturnsBadRequest()
    {
        var runReq = new CreateTestRunRequest("run_neg_dur", "UnitTests", "Development");
        var runRes = await _client.PostAsJsonAsync("/api/v1/test-runs", runReq);
        var run = await runRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(run);

        var invalidReq = new CreateTestResultRequest(
            TestName: "test_invalid_dur",
            TestCaseId: null,
            Status: TestStatus.Passed,
            Duration: -1.5,
            ErrorMessage: null
        );
        var res = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run.Id}/results", invalidReq);
        Assert.Equal(HttpStatusCode.BadRequest, res.StatusCode);
    }
}
