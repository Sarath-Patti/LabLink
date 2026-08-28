using System.Net;
using System.Net.Http.Json;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class DutApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public DutApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.UseSetting("Persistence:Provider", "InMemory");
        }).CreateClient();
    }

    [Fact]
    public async Task RegisterDut_ValidRequest_ReturnsCreatedAndDutDto()
    {
        var request = new CreateDutRequest(
            SerialNumber: $"SN-UNIT-{Guid.NewGuid().ToString()[..8]}",
            PartNumber: "PN-OPT-100G",
            HardwareRevision: "RevB",
            FirmwareVersion: "v1.4.2"
        );

        var response = await _client.PostAsJsonAsync("/api/v1/duts", request);
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var dto = await response.Content.ReadFromJsonAsync<DutDto>();
        Assert.NotNull(dto);
        Assert.Equal(request.SerialNumber, dto.SerialNumber);
        Assert.Equal(request.PartNumber, dto.PartNumber);
        Assert.Equal("Untested", dto.Status);
    }

    [Fact]
    public async Task RegisterDut_DuplicateSerial_ReturnsConflict()
    {
        var serial = $"SN-DUP-{Guid.NewGuid().ToString()[..8]}";
        var request = new CreateDutRequest(serial, "PN-1", "RevA", "v1.0");

        var response1 = await _client.PostAsJsonAsync("/api/v1/duts", request);
        Assert.Equal(HttpStatusCode.Created, response1.StatusCode);

        var response2 = await _client.PostAsJsonAsync("/api/v1/duts", request);
        Assert.Equal(HttpStatusCode.Conflict, response2.StatusCode);
    }

    [Fact]
    public async Task GetDutBySerial_ExistingSerial_ReturnsDutDto()
    {
        var serial = $"SN-GET-{Guid.NewGuid().ToString()[..8]}";
        var request = new CreateDutRequest(serial, "PN-2", "RevA", "v1.0");
        await _client.PostAsJsonAsync("/api/v1/duts", request);

        var response = await _client.GetAsync($"/api/v1/duts/serial/{serial}");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var dto = await response.Content.ReadFromJsonAsync<DutDto>();
        Assert.NotNull(dto);
        Assert.Equal(serial, dto.SerialNumber);
    }
}
