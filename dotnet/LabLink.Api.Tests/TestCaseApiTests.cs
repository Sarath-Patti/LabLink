using System.Net;
using System.Net.Http.Json;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class TestCaseApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public TestCaseApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task TestCase_Lifecycle_CreateGetListValidation_Succeeds()
    {
        // 1. Create TestCase
        var request = new CreateTestCaseRequest(
            Name: "test_opm_wavelength_tuning",
            Description: "Verify OPM wavelength calibration",
            Suite: "functional",
            Category: "optical"
        );

        var createRes = await _client.PostAsJsonAsync("/api/v1/test-cases", request);
        Assert.Equal(HttpStatusCode.Created, createRes.StatusCode);

        var created = await createRes.Content.ReadFromJsonAsync<TestCaseResponse>();
        Assert.NotNull(created);
        Assert.Equal("test_opm_wavelength_tuning", created.Name);

        // 2. Get By Id
        var getRes = await _client.GetAsync($"/api/v1/test-cases/{created.Id}");
        Assert.Equal(HttpStatusCode.OK, getRes.StatusCode);

        var retrieved = await getRes.Content.ReadFromJsonAsync<TestCaseResponse>();
        Assert.NotNull(retrieved);
        Assert.Equal(created.Id, retrieved.Id);

        // 3. List TestCases
        var listRes = await _client.GetAsync("/api/v1/test-cases");
        Assert.Equal(HttpStatusCode.OK, listRes.StatusCode);

        var list = await listRes.Content.ReadFromJsonAsync<List<TestCaseResponse>>();
        Assert.NotNull(list);
        Assert.Contains(list, t => t.Id == created.Id);

        // 4. Missing ID returns 404
        var missingRes = await _client.GetAsync("/api/v1/test-cases/nonexistent_id_999");
        Assert.Equal(HttpStatusCode.NotFound, missingRes.StatusCode);

        // 5. Invalid Empty Name returns 400
        var invalidReq = new CreateTestCaseRequest(Name: "");
        var invalidRes = await _client.PostAsJsonAsync("/api/v1/test-cases", invalidReq);
        Assert.Equal(HttpStatusCode.BadRequest, invalidRes.StatusCode);
    }
}
