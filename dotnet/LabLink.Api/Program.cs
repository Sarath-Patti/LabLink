using System.Text.Json.Serialization;
using LabLink.Api.Middleware;
using LabLink.Api.Persistence;
using LabLink.Api.Repositories;
using LabLink.Api.Repositories.Postgres;
using LabLink.Api.Services;
using Microsoft.EntityFrameworkCore;

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

// Configure Persistence Provider based on AppSettings
var persistenceProvider = builder.Configuration["Persistence:Provider"] ?? "PostgreSQL";
var connectionString = builder.Configuration.GetConnectionString("LabLinkDatabase");

if (persistenceProvider.Equals("PostgreSQL", StringComparison.OrdinalIgnoreCase))
{
    builder.Services.AddDbContext<LabLinkDbContext>(options =>
    {
        options.UseNpgsql(connectionString);
    });

    builder.Services.AddScoped<ITestCaseRepository, PostgresTestCaseRepository>();
    builder.Services.AddScoped<ITestRunRepository, PostgresTestRunRepository>();
    builder.Services.AddScoped<ITestResultRepository, PostgresTestResultRepository>();
    builder.Services.AddScoped<IDeviceRepository, PostgresDeviceRepository>();
    builder.Services.AddScoped<IInstrumentRepository, PostgresInstrumentRepository>();
    builder.Services.AddScoped<IDutRepository, PostgresDutRepository>();
    builder.Services.AddScoped<IManufacturingRunRepository, PostgresManufacturingRunRepository>();
    builder.Services.AddScoped<IMeasurementRepository, PostgresMeasurementRepository>();
}
else
{
    builder.Services.AddSingleton<ITestCaseRepository, InMemoryTestCaseRepository>();
    builder.Services.AddSingleton<ITestRunRepository, InMemoryTestRunRepository>();
    builder.Services.AddSingleton<ITestResultRepository, InMemoryTestResultRepository>();
    builder.Services.AddSingleton<IDeviceRepository, InMemoryDeviceRepository>();
    builder.Services.AddSingleton<IInstrumentRepository, InMemoryInstrumentRepository>();
    builder.Services.AddSingleton<IDutRepository, InMemoryDutRepository>();
    builder.Services.AddSingleton<IManufacturingRunRepository, InMemoryManufacturingRunRepository>();
    builder.Services.AddSingleton<IMeasurementRepository, InMemoryMeasurementRepository>();
}

// Register Application Services (Scoped for compatibility with DbContext)
builder.Services.AddScoped<TestCaseService>();
builder.Services.AddScoped<TestRunService>();
builder.Services.AddScoped<TestResultService>();
builder.Services.AddScoped<DeviceService>();
builder.Services.AddScoped<InstrumentService>();
builder.Services.AddScoped<DutService>();
builder.Services.AddScoped<ManufacturingService>();

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
