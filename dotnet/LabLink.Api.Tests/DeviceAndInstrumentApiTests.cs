using System.Net;
using System.Net.Http.Json;
using LabLink.Api.Domain.Enums;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class DeviceAndInstrumentApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public DeviceAndInstrumentApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.UseSetting("Persistence:Provider", "InMemory");
        }).CreateClient();
    }

    [Fact]
    public async Task Device_CreationAndRetrieval_Succeeds()
    {
        var request = new CreateDeviceRequest(
            Name: "core_nexus_switch_01",
            Type: DeviceType.NetworkSwitch,
            Model: "Cisco-Nexus-9000",
            Address: "192.168.1.50:5025",
            Protocol: DeviceProtocol.SCPI,
            Enabled: true,
            Metadata: new Dictionary<string, string> { ["vlan_mode"] = "trunk" }
        );

        var createRes = await _client.PostAsJsonAsync("/api/v1/devices", request);
        Assert.Equal(HttpStatusCode.Created, createRes.StatusCode);

        var created = await createRes.Content.ReadFromJsonAsync<DeviceResponse>();
        Assert.NotNull(created);
        Assert.Equal("core_nexus_switch_01", created.Name);

        var getRes = await _client.GetAsync($"/api/v1/devices/{created.Id}");
        Assert.Equal(HttpStatusCode.OK, getRes.StatusCode);
    }

    [Fact]
    public async Task Instrument_CreationAndRetrieval_Succeeds()
    {
        var request = new CreateInstrumentRequest(
            Name: "optical_power_meter_lab1",
            Type: "OpticalPowerMeter",
            Interface: "TCPIP",
            Address: "127.0.0.1:5025"
        );

        var createRes = await _client.PostAsJsonAsync("/api/v1/instruments", request);
        Assert.Equal(HttpStatusCode.Created, createRes.StatusCode);

        var created = await createRes.Content.ReadFromJsonAsync<InstrumentResponse>();
        Assert.NotNull(created);
        Assert.Equal("optical_power_meter_lab1", created.Name);

        var getRes = await _client.GetAsync($"/api/v1/instruments/{created.Id}");
        Assert.Equal(HttpStatusCode.OK, getRes.StatusCode);
    }
}
