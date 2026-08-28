using System.Text.Json.Serialization;
using LabLink.Api.Middleware;
using LabLink.Api.Repositories;
using LabLink.Api.Services;

var builder = WebApplication.CreateBuilder(args);

// Add framework services with string enum JSON converter
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    });

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "LabLink Test Management API",
        Version = "v1",
        Description = "LabLink C#/.NET Test Orchestration & Management API Layer"
    });
});

// Register In-Memory Repositories (Singleton for persistent in-memory session state across requests)
builder.Services.AddSingleton<ITestCaseRepository, InMemoryTestCaseRepository>();
builder.Services.AddSingleton<ITestRunRepository, InMemoryTestRunRepository>();
builder.Services.AddSingleton<ITestResultRepository, InMemoryTestResultRepository>();
builder.Services.AddSingleton<IDeviceRepository, InMemoryDeviceRepository>();
builder.Services.AddSingleton<IInstrumentRepository, InMemoryInstrumentRepository>();

// Register Application Services
builder.Services.AddSingleton<TestCaseService>();
builder.Services.AddSingleton<TestRunService>();
builder.Services.AddSingleton<TestResultService>();
builder.Services.AddSingleton<DeviceService>();
builder.Services.AddSingleton<InstrumentService>();

var app = builder.Build();

// Exception middleware
app.UseMiddleware<ApiExceptionMiddleware>();

// Enable Swagger / OpenAPI documentation
app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "LabLink API v1");
});

app.UseRouting();
app.UseAuthorization();
app.MapControllers();

app.Run();

// Make Program class accessible to WebApplicationFactory integration tests
public partial class Program { }
