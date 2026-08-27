using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class HealthController : ControllerBase
{
    [HttpGet]
    public IActionResult GetStatus()
    {
        return Ok(new
        {
            status = "Healthy",
            service = "LabLink.Api",
            version = "0.1.0",
            timestamp = DateTime.UtcNow
        });
    }
}
