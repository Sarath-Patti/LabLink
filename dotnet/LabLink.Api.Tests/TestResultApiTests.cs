using System.Net;
using System.Net.Http.Json;
using LabLink.Api.Domain.Enums;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class TestResultApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public TestResultApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task TestResult_Ingestion_Aggregation_And_Validation()
    {
        // 1. Create TestRun
        var runReq = new CreateTestRunRequest(Name: "result_ingestion_run");
        var runRes = await _client.PostAsJsonAsync("/api/v1/test-runs", runReq);
        var run = await runRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(run);

        // 2. Submit Result 1 (Passed)
        var res1Req = new CreateTestResultRequest(
            TestName: "test_opm_power_measurement",
            TestCaseId: null,
            Status: TestStatus.Passed,
            Duration: 0.15,
            ErrorMessage: null
        );
        var res1 = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run.Id}/results", res1Req);
        Assert.Equal(HttpStatusCode.Created, res1.StatusCode);

        // 3. Submit Result 2 (Failed)
        var res2Req = new CreateTestResultRequest(
            TestName: "test_optical_switch_route_failure",
            TestCaseId: null,
            Status: TestStatus.Failed,
            Duration: 0.45,
            ErrorMessage: "Route timeout"
        );
        var res2 = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run.Id}/results", res2Req);
        Assert.Equal(HttpStatusCode.Created, res2.StatusCode);

        // 4. Retrieve Results
        var getResults = await _client.GetAsync($"/api/v1/test-runs/{run.Id}/results");
        Assert.Equal(HttpStatusCode.OK, getResults.StatusCode);

        var resultsList = await getResults.Content.ReadFromJsonAsync<List<TestResultResponse>>();
        Assert.NotNull(resultsList);
        Assert.Equal(2, resultsList.Count);

        // 5. Complete Run and check Aggregated Metrics
        var completeRes = await _client.PostAsJsonAsync(
            $"/api/v1/test-runs/{run.Id}/complete",
            new CompleteTestRunRequest()
        );
        var completedRun = await completeRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(completedRun);
        Assert.Equal(2, completedRun.TotalTests);
        Assert.Equal(1, completedRun.PassedTests);
        Assert.Equal(1, completedRun.FailedTests);
        Assert.Equal(0, completedRun.SkippedTests);

        // 6. Negative Duration -> 400 Bad Request
        var invalidReq = new CreateTestResultRequest(
            TestName: "test_negative_duration",
            TestCaseId: null,
            Status: TestStatus.Passed,
            Duration: -5.0,
            ErrorMessage: null
        );

        // Create new active run for testing negative duration
        var run2Res = await _client.PostAsJsonAsync("/api/v1/test-runs", new CreateTestRunRequest("run_neg_dur"));
        var run2 = await run2Res.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(run2);

        var negDurRes = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run2.Id}/results", invalidReq);
        Assert.Equal(HttpStatusCode.BadRequest, negDurRes.StatusCode);
    }
}
