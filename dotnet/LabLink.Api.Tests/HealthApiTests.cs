using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class HealthApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public HealthApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetHealth_ReturnsStatus200AndHealthyPayload()
    {
        var response = await _client.GetAsync("/api/v1/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var doc = await response.Content.ReadFromJsonAsync<JsonElement>();
        Assert.Equal("Healthy", doc.GetProperty("status").GetString());
        Assert.Equal("LabLink.Api", doc.GetProperty("service").GetString());
        Assert.Equal("1.0.0", doc.GetProperty("version").GetString());
    }
}
