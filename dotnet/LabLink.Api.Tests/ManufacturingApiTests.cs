using System.Net;
using System.Net.Http.Json;
using LabLink.Api.DTOs;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace LabLink.Api.Tests;

public class ManufacturingApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public ManufacturingApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.UseSetting("Persistence:Provider", "InMemory");
        }).CreateClient();
    }

    [Fact]
    public async Task ManufacturingRun_FullLifecycleWorkflow_PassesAndPersists()
    {
        var serial = $"SN-MFG-{Guid.NewGuid().ToString()[..8]}";

        // 1. Create Manufacturing Run
        var createRequest = new CreateManufacturingRunRequest(
            SerialNumber: serial,
            StationId: "Station-Optical-01",
            SequenceName: "OpticalModuleTestSequence",
            SequenceVersion: "1.2",
            SoftwareVersion: "1.0.0"
        );

        var createResponse = await _client.PostAsJsonAsync("/api/v1/manufacturing/runs", createRequest);
        Assert.Equal(HttpStatusCode.Created, createResponse.StatusCode);
        var runDto = await createResponse.Content.ReadFromJsonAsync<ManufacturingRunDto>();
        Assert.NotNull(runDto);
        Assert.Equal(serial, runDto.SerialNumber);
        Assert.True(runDto.FirstPass);

        var runId = runDto.Id;

        // 2. Add Measurement Records
        var meas1 = new AddMeasurementRequest(
            StepName: "Optical Power Sweep",
            MeasurementName: "optical_power_dbm",
            Value: -3.4,
            Unit: "dBm",
            LowerLimit: -5.0,
            UpperLimit: -1.0,
            ExpectedValue: null,
            Verdict: "Passed",
            FailureCode: "NONE",
            InstrumentSource: "OpticalPowerMeter"
        );

        var measResponse1 = await _client.PostAsJsonAsync($"/api/v1/manufacturing/runs/{runId}/measurements", meas1);
        Assert.Equal(HttpStatusCode.Created, measResponse1.StatusCode);

        // 3. Complete Run
        var completeRequest = new CompleteManufacturingRunRequest(
            Verdict: "Completed",
            FailureCode: "NONE",
            FailureSummary: "All optical manufacturing steps passed limits"
        );

        var completeResponse = await _client.PostAsJsonAsync($"/api/v1/manufacturing/runs/{runId}/complete", completeRequest);
        Assert.Equal(HttpStatusCode.OK, completeResponse.StatusCode);

        var completedDto = await completeResponse.Content.ReadFromJsonAsync<ManufacturingRunDto>();
        Assert.NotNull(completedDto);
        Assert.Equal("Completed", completedDto.Verdict);
        Assert.Equal("NONE", completedDto.FailureCode);

        // 4. Retrieve Yield Analytics
        var yieldResponse = await _client.GetAsync("/api/v1/manufacturing/analytics/yield");
        Assert.Equal(HttpStatusCode.OK, yieldResponse.StatusCode);

        var yieldDto = await yieldResponse.Content.ReadFromJsonAsync<YieldAnalyticsDto>();
        Assert.NotNull(yieldDto);
        Assert.True(yieldDto.TotalUnitsTested > 0);
    }
}
