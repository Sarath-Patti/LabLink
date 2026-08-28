using LabLink.Api.DTOs;
using LabLink.Api.Services;
using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/test-runs/{testRunId}/results")]
public class TestResultsController : ControllerBase
{
    private readonly TestResultService _service;

    public TestResultsController(TestResultService service)
    {
        _service = service;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<TestResultResponse>>> GetResults(string testRunId)
    {
        var results = await _service.GetResultsByRunIdAsync(testRunId);
        return Ok(results);
    }

    [HttpPost]
    public async Task<ActionResult<TestResultResponse>> IngestResult(
        string testRunId,
        [FromBody] CreateTestResultRequest request
    )
    {
        var result = await _service.IngestResultAsync(testRunId, request);
        return CreatedAtAction(nameof(GetResults), new { testRunId }, result);
    }
}
