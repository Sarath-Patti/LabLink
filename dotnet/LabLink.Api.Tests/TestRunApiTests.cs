using System.Net;
using System.Net.Http.Json;
using LabLink.Api.Domain.Enums;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class TestRunApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public TestRunApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task TestRun_Lifecycle_CreateCompleteInvalidTransitions()
    {
        // 1. Create TestRun
        var createReq = new CreateTestRunRequest(
            Name: "nightly_regression_sweep",
            Trigger: "CI/CD",
            Environment: "Staging"
        );

        var createRes = await _client.PostAsJsonAsync("/api/v1/test-runs", createReq);
        Assert.Equal(HttpStatusCode.Created, createRes.StatusCode);

        var created = await createRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(created);
        Assert.Equal("Created", created.Status);

        // 2. Complete TestRun
        var completeReq = new CompleteTestRunRequest(Status: TestRunStatus.Completed);
        var completeRes = await _client.PostAsJsonAsync($"/api/v1/test-runs/{created.Id}/complete", completeReq);
        Assert.Equal(HttpStatusCode.OK, completeRes.StatusCode);

        var completed = await completeRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(completed);
        Assert.Equal("Completed", completed.Status);
        Assert.NotNull(completed.CompletedAt);

        // 3. Attempt Invalid Transition on Completed Run -> 409 Conflict
        var invalidCompleteRes = await _client.PostAsJsonAsync($"/api/v1/test-runs/{created.Id}/complete", completeReq);
        Assert.Equal(HttpStatusCode.Conflict, invalidCompleteRes.StatusCode);
    }
}
