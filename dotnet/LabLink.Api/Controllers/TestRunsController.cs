using LabLink.Api.DTOs;
using LabLink.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/test-runs")]
public class TestRunsController : ControllerBase
{
    private readonly TestRunService _service;

    public TestRunsController(TestRunService service)
    {
        _service = service;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<TestRunResponse>>> GetAll()
    {
        var runs = await _service.GetAllAsync();
        return Ok(runs);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<TestRunResponse>> GetById(string id)
    {
        var run = await _service.GetByIdAsync(id);
        return Ok(run);
    }

    [HttpPost]
    public async Task<ActionResult<TestRunResponse>> Create([FromBody] CreateTestRunRequest request)
    {
        var created = await _service.CreateAsync(request);
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    [HttpPost("{id}/complete")]
    public async Task<ActionResult<TestRunResponse>> Complete(string id, [FromBody] CompleteTestRunRequest request)
    {
        var completed = await _service.CompleteRunAsync(id, request);
        return Ok(completed);
    }
}
