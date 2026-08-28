using LabLink.Api.DTOs;
using LabLink.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/instruments")]
public class InstrumentsController : ControllerBase
{
    private readonly InstrumentService _service;

    public InstrumentsController(InstrumentService service)
    {
        _service = service;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<InstrumentResponse>>> GetAll()
    {
        var instruments = await _service.GetAllAsync();
        return Ok(instruments);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<InstrumentResponse>> GetById(string id)
    {
        var instrument = await _service.GetByIdAsync(id);
        return Ok(instrument);
    }

    [HttpPost]
    public async Task<ActionResult<InstrumentResponse>> Create([FromBody] CreateInstrumentRequest request)
    {
        var created = await _service.CreateAsync(request);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }
}
