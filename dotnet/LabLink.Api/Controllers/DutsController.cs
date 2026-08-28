using LabLink.Api.DTOs;
using LabLink.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class DutsController : ControllerBase
{
    private readonly DutService _dutService;

    public DutsController(DutService dutService)
    {
        _dutService = dutService;
    }

    [HttpPost]
    public async Task<IActionResult> RegisterDut([FromBody] CreateDutRequest request)
    {
        var created = await _dutService.RegisterDutAsync(request);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(string id)
    {
        var dut = await _dutService.GetDutByIdAsync(id);
        return Ok(dut);
    }

    [HttpGet("serial/{serialNumber}")]
    public async Task<IActionResult> GetBySerialNumber(string serialNumber)
    {
        var dut = await _dutService.GetDutBySerialNumberAsync(serialNumber);
        return Ok(dut);
    }

    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var duts = await _dutService.GetAllDutsAsync();
        return Ok(duts);
    }
}
