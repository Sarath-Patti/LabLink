using LabLink.Api.Domain.Enums;
using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using LabLink.Api.Repositories;

using Microsoft.EntityFrameworkCore;

using Xunit;

namespace LabLink.Api.Tests;

public class PostgresManufacturingIntegrationTests
{
    private const string ConnectionString = "Host=localhost;Port=5432;Database=lablink_test;Username=sarathpatti;";

    private DbContextOptions<LabLinkDbContext> CreateOptions()
    {
        return new DbContextOptionsBuilder<LabLinkDbContext>()
            .UseNpgsql(ConnectionString)
            .Options;
    }

    [Fact]
    public async Task PostgresDutRepository_CRUD_Operations_WorkSynchronously()
    {
        var options = CreateOptions();
        var serial = $"SN-PG-{Guid.NewGuid().ToString()[..8]}";
        string dutId;

        await using (var context = new LabLinkDbContext(options))
        {
            var repo = new PostgresDutRepository(context);
            var dut = new Dut
            {
                SerialNumber = serial,
                PartNumber = "PN-100G",
                HardwareRevision = "RevC",
                FirmwareVersion = "v2.0.0",
                Status = DutStatus.Untested
            };
            var added = await repo.AddAsync(dut);
            dutId = added.Id;
        }

        await using (var context = new LabLinkDbContext(options))
        {
            var repo = new PostgresDutRepository(context);
            var fetched = await repo.GetBySerialNumberAsync(serial);
            Assert.NotNull(fetched);
            Assert.Equal("PN-100G", fetched.PartNumber);

            fetched.Status = DutStatus.Passed;
            await repo.UpdateAsync(fetched);
        }

        await using (var context = new LabLinkDbContext(options))
        {
            var repo = new PostgresDutRepository(context);
            var updated = await repo.GetByIdAsync(dutId);
            Assert.Equal(DutStatus.Passed, updated!.Status);
        }
    }

    [Fact]
    public async Task PostgresManufacturingRunRepository_RunAndMeasurement_PersistCorrectly()
    {
        var options = CreateOptions();
        var serial = $"SN-MFG-PG-{Guid.NewGuid().ToString()[..8]}";
        string runId;

        await using (var context = new LabLinkDbContext(options))
        {
            var dutRepo = new PostgresDutRepository(context);
            var runRepo = new PostgresManufacturingRunRepository(context);
            var measRepo = new PostgresMeasurementRepository(context);

            var dut = await dutRepo.AddAsync(new Dut { SerialNumber = serial });

            var run = await runRepo.AddAsync(new ManufacturingRun
            {
                DutId = dut.Id,
                SerialNumber = dut.SerialNumber,
                StationId = "Station-02",
                SequenceName = "PostgresTestSequence",
                SequenceVersion = "1.0",
                Verdict = TestRunStatus.Running,
                FirstPass = true
            });

            runId = run.Id;

            await measRepo.AddAsync(new MeasurementRecord
            {
                ManufacturingRunId = run.Id,
                DutId = dut.Id,
                StepName = "Optical Power Test",
                MeasurementName = "power_dbm",
                Value = -2.1,
                Unit = "dBm",
                LowerLimit = -4.0,
                UpperLimit = -1.0,
                Verdict = TestStatus.Passed,
                FailureCode = FailureCode.NONE,
                InstrumentSource = "OPM_Simulator"
            });
        }

        await using (var context = new LabLinkDbContext(options))
        {
            var measRepo = new PostgresMeasurementRepository(context);
            var records = (await measRepo.GetByRunIdAsync(runId)).ToList();
            Assert.Single(records);
            Assert.Equal("power_dbm", records.First().MeasurementName);
        }
    }
}
