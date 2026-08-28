using System.Net;
using System.Net.Http.Json;
using LabLink.Api.Domain.Enums;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class TestRunApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public TestRunApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.UseSetting("Persistence:Provider", "InMemory");
        }).CreateClient();
    }

    [Fact]
    public async Task TestRun_FullLifecycle_CreateCompleteRetrieve_Succeeds()
    {
        var createReq = new CreateTestRunRequest("nightly_regression_sweep", "JenkinsCI", "ProductionLab");
        var createRes = await _client.PostAsJsonAsync("/api/v1/test-runs", createReq);
        Assert.Equal(HttpStatusCode.Created, createRes.StatusCode);

        var run = await createRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(run);
        Assert.Equal("nightly_regression_sweep", run.Name);
        Assert.Equal("Created", run.Status);

        var completeRes = await _client.PostAsJsonAsync($"/api/v1/test-runs/{run.Id}/complete", new CompleteTestRunRequest(TestRunStatus.Completed));
        Assert.Equal(HttpStatusCode.OK, completeRes.StatusCode);

        var completed = await completeRes.Content.ReadFromJsonAsync<TestRunResponse>();
        Assert.NotNull(completed);
        Assert.Equal("Completed", completed.Status);
    }
}
