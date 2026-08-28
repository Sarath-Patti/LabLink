using System.Net;
using System.Net.Http.Json;
using LabLink.Api.Domain.Enums;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class DeviceAndInstrumentApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public DeviceAndInstrumentApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
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
            Enabled: true
        );

        var createRes = await _client.PostAsJsonAsync("/api/v1/devices", request);
        Assert.Equal(HttpStatusCode.Created, createRes.StatusCode);

        var created = await createRes.Content.ReadFromJsonAsync<DeviceResponse>();
        Assert.NotNull(created);
        Assert.Equal("core_nexus_switch_01", created.Name);

        var listRes = await _client.GetAsync("/api/v1/devices");
        Assert.Equal(HttpStatusCode.OK, listRes.StatusCode);

        var list = await listRes.Content.ReadFromJsonAsync<List<DeviceResponse>>();
        Assert.NotNull(list);
        Assert.Contains(list, d => d.Id == created.Id);
    }

    [Fact]
    public async Task Instrument_CreationAndRetrieval_Succeeds()
    {
        var request = new CreateInstrumentRequest(
            Name: "optical_power_meter_lab1",
            Type: "OpticalPowerMeter",
            Model: "Keysight-N5767A",
            Interface: "TCPIP",
            Address: "127.0.0.1:5025",
            Enabled: true
        );

        var createRes = await _client.PostAsJsonAsync("/api/v1/instruments", request);
        Assert.Equal(HttpStatusCode.Created, createRes.StatusCode);

        var created = await createRes.Content.ReadFromJsonAsync<InstrumentResponse>();
        Assert.NotNull(created);
        Assert.Equal("optical_power_meter_lab1", created.Name);

        var listRes = await _client.GetAsync("/api/v1/instruments");
        Assert.Equal(HttpStatusCode.OK, listRes.StatusCode);

        var list = await listRes.Content.ReadFromJsonAsync<List<InstrumentResponse>>();
        Assert.NotNull(list);
        Assert.Contains(list, i => i.Id == created.Id);
    }
}
