using LabLink.Api.DTOs;
using LabLink.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class ManufacturingController : ControllerBase
{
    private readonly ManufacturingService _manufacturingService;

    public ManufacturingController(ManufacturingService manufacturingService)
    {
        _manufacturingService = manufacturingService;
    }

    [HttpPost("runs")]
    public async Task<IActionResult> CreateRun([FromBody] CreateManufacturingRunRequest request)
    {
        var created = await _manufacturingService.CreateRunAsync(request);
        return CreatedAtAction(nameof(GetRunById), new { id = created.Id }, created);
    }

    [HttpGet("runs/{id}")]
    public async Task<IActionResult> GetRunById(string id)
    {
        var run = await _manufacturingService.GetRunByIdAsync(id);
        return Ok(run);
    }

    [HttpPost("runs/{id}/measurements")]
    public async Task<IActionResult> AddMeasurement(string id, [FromBody] AddMeasurementRequest request)
    {
        var record = await _manufacturingService.AddMeasurementAsync(id, request);
        return Created($"/api/v1/manufacturing/runs/{id}/measurements/{record.Id}", record);
    }

    [HttpPost("runs/{id}/complete")]
    public async Task<IActionResult> CompleteRun(string id, [FromBody] CompleteManufacturingRunRequest request)
    {
        var completed = await _manufacturingService.CompleteRunAsync(id, request);
        return Ok(completed);
    }

    [HttpGet("runs/{id}/measurements")]
    public async Task<IActionResult> GetRunMeasurements(string id)
    {
        var records = await _manufacturingService.GetRunMeasurementsAsync(id);
        return Ok(records);
    }

    [HttpGet("analytics/yield")]
    public async Task<IActionResult> GetYieldAnalytics()
    {
        var analytics = await _manufacturingService.GetYieldAnalyticsAsync();
        return Ok(analytics);
    }
}
