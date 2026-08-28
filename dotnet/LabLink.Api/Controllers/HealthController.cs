using LabLink.Api.Persistence;
using Microsoft.AspNetCore.Mvc;

namespace LabLink.Api.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class HealthController : ControllerBase
{
    private readonly IServiceProvider _serviceProvider;

    public HealthController(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    [HttpGet]
    public async Task<IActionResult> GetStatus()
    {
        var dbStatus = "InMemory";

        using (var scope = _serviceProvider.CreateScope())
        {
            var dbContext = scope.ServiceProvider.GetService<LabLinkDbContext>();
            if (dbContext != null)
            {
                try
                {
                    var canConnect = await dbContext.Database.CanConnectAsync();
                    dbStatus = canConnect ? "Connected" : "Disconnected";
                }
                catch
                {
                    dbStatus = "Error";
                }
            }
        }

        return Ok(new
        {
            status = "Healthy",
            service = "LabLink.Api",
            version = "1.0.0",
            database = dbStatus,
            timestamp = DateTime.UtcNow
        });
    }
}
