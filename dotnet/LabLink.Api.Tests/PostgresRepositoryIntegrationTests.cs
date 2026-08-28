using LabLink.Api.Domain.Enums;
using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using LabLink.Api.Repositories.Postgres;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace LabLink.Api.Tests;

public class PostgresRepositoryIntegrationTests
{
    private const string ConnectionString = "Host=localhost;Port=5432;Database=lablink_test;Username=sarathpatti;";

    private DbContextOptions<LabLinkDbContext> CreateOptions()
    {
        return new DbContextOptionsBuilder<LabLinkDbContext>()
            .UseNpgsql(ConnectionString)
            .Options;
    }

    [Fact]
    public async Task Postgres_Migration_And_TestCase_CRUD_Succeeds()
    {
        var options = CreateOptions();

        // 1. Ensure migrations applied
        await using (var context = new LabLinkDbContext(options))
        {
            await context.Database.MigrateAsync();
        }

        var testCaseId = Guid.NewGuid().ToString();

        // 2. Insert TestCase using PostgresTestCaseRepository instance 1
        await using (var context = new LabLinkDbContext(options))
        {
            var repo = new PostgresTestCaseRepository(context);
            var tc = new TestCase
            {
                Id = testCaseId,
                Name = "test_postgres_optical_opm",
                Description = "Postgres integration test case",
                Suite = "functional",
                Category = "optical"
            };
            await repo.AddAsync(tc);
        }

        // 3. Retrieve TestCase using fresh PostgresTestCaseRepository instance 2 (Verifies DB Persistence)
        await using (var context = new LabLinkDbContext(options))
        {
            var repo = new PostgresTestCaseRepository(context);
            var retrieved = await repo.GetByIdAsync(testCaseId);

            Assert.NotNull(retrieved);
            Assert.Equal("test_postgres_optical_opm", retrieved.Name);
            Assert.Equal("functional", retrieved.Suite);
        }
    }

    [Fact]
    public async Task Postgres_TestRun_And_TestResults_RelationalPersistence_Succeeds()
    {
        var options = CreateOptions();
        var runId = Guid.NewGuid().ToString();
        var res1Id = Guid.NewGuid().ToString();
        var res2Id = Guid.NewGuid().ToString();

        // 1. Add TestRun and TestResults across distinct repositories
        await using (var context = new LabLinkDbContext(options))
        {
            var runRepo = new PostgresTestRunRepository(context);
            var resultRepo = new PostgresTestResultRepository(context);

            var run = new TestRun
            {
                Id = runId,
                Name = "postgres_relational_test_run",
                Status = TestRunStatus.Created,
                StartedAt = DateTime.UtcNow,
                Trigger = "xUnit",
                Environment = "Test"
            };
            await runRepo.AddAsync(run);

            await resultRepo.AddAsync(new TestResult
            {
                Id = res1Id,
                TestRunId = runId,
                TestCaseId = null,
                TestName = "test_step_1",
                Status = TestStatus.Passed,
                Duration = 0.25,
                Timestamp = DateTime.UtcNow
            });

            await resultRepo.AddAsync(new TestResult
            {
                Id = res2Id,
                TestRunId = runId,
                TestCaseId = null,
                TestName = "test_step_2",
                Status = TestStatus.Failed,
                Duration = 0.85,
                ErrorMessage = "Route timeout",
                Timestamp = DateTime.UtcNow
            });
        }

        // 2. Query and assert relational integrity across fresh context instance
        await using (var context = new LabLinkDbContext(options))
        {
            var runRepo = new PostgresTestRunRepository(context);
            var resultRepo = new PostgresTestResultRepository(context);

            var run = await runRepo.GetByIdAsync(runId);
            Assert.NotNull(run);

            var results = (await resultRepo.GetByTestRunIdAsync(runId)).ToList();
            Assert.Equal(2, results.Count);
            Assert.Contains(results, r => r.Id == res1Id && r.Status == TestStatus.Passed);
            Assert.Contains(results, r => r.Id == res2Id && r.Status == TestStatus.Failed);
        }
    }

    [Fact]
    public async Task Postgres_Device_JSON_Metadata_Persistence_Succeeds()
    {
        var options = CreateOptions();
        var deviceId = Guid.NewGuid().ToString();

        await using (var context = new LabLinkDbContext(options))
        {
            var repo = new PostgresDeviceRepository(context);
            var device = new Device
            {
                Id = deviceId,
                Name = "nexus_9000_postgres",
                Type = DeviceType.NetworkSwitch,
                Model = "N9K-C93180YC-EX",
                Address = "192.168.1.100:5025",
                Protocol = DeviceProtocol.SCPI,
                Enabled = true,
                Metadata = new Dictionary<string, string>
                {
                    ["firmware"] = "v9.3.5",
                    ["location"] = "Rack-B4"
                }
            };
            await repo.AddAsync(device);
        }

        await using (var context = new LabLinkDbContext(options))
        {
            var repo = new PostgresDeviceRepository(context);
            var retrieved = await repo.GetByIdAsync(deviceId);

            Assert.NotNull(retrieved);
            Assert.Equal("nexus_9000_postgres", retrieved.Name);
            Assert.Equal("v9.3.5", retrieved.Metadata["firmware"]);
            Assert.Equal("Rack-B4", retrieved.Metadata["location"]);
        }
    }
}
