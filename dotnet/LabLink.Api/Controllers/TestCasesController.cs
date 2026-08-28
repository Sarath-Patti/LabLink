using LabLink.Api.DTOs;
using LabLink.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/test-cases")]
public class TestCasesController : ControllerBase
{
    private readonly TestCaseService _service;

    public TestCasesController(TestCaseService service)
    {
        _service = service;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<TestCaseResponse>>> GetAll()
    {
        var items = await _service.GetAllAsync();
        return Ok(items);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<TestCaseResponse>> GetById(string id)
    {
        var item = await _service.GetByIdAsync(id);
        return Ok(item);
    }

    [HttpPost]
    public async Task<ActionResult<TestCaseResponse>> Create([FromBody] CreateTestCaseRequest request)
    {
        var created = await _service.CreateAsync(request);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }
}
