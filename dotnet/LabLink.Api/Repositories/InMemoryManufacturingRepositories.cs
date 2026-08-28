using System.Collections.Concurrent;
using LabLink.Api.Domain.Models;

namespace LabLink.Api.Repositories;

public class InMemoryDutRepository : IDutRepository
{
    private readonly ConcurrentDictionary<string, Dut> _duts = new();

    public Task<Dut?> GetByIdAsync(string id)
    {
        _duts.TryGetValue(id, out var dut);
        return Task.FromResult(dut);
    }

    public Task<Dut?> GetBySerialNumberAsync(string serialNumber)
    {
        var dut = _duts.Values.FirstOrDefault(d => d.SerialNumber.Equals(serialNumber, StringComparison.OrdinalIgnoreCase));
        return Task.FromResult(dut);
    }

    public Task<IEnumerable<Dut>> GetAllAsync()
    {
        return Task.FromResult<IEnumerable<Dut>>(_duts.Values);
    }

    public Task<Dut> AddAsync(Dut dut)
    {
        _duts[dut.Id] = dut;
        return Task.FromResult(dut);
    }

    public Task<Dut> UpdateAsync(Dut dut)
    {
        _duts[dut.Id] = dut;
        return Task.FromResult(dut);
    }
}

public class InMemoryManufacturingRunRepository : IManufacturingRunRepository
{
    private readonly ConcurrentDictionary<string, ManufacturingRun> _runs = new();

    public Task<ManufacturingRun?> GetByIdAsync(string id)
    {
        _runs.TryGetValue(id, out var run);
        return Task.FromResult(run);
    }

    public Task<IEnumerable<ManufacturingRun>> GetByDutIdAsync(string dutId)
    {
        var runs = _runs.Values.Where(r => r.DutId == dutId);
        return Task.FromResult(runs);
    }

    public Task<IEnumerable<ManufacturingRun>> GetBySerialNumberAsync(string serialNumber)
    {
        var runs = _runs.Values.Where(r => r.SerialNumber.Equals(serialNumber, StringComparison.OrdinalIgnoreCase));
        return Task.FromResult(runs);
    }

    public Task<IEnumerable<ManufacturingRun>> GetAllAsync()
    {
        return Task.FromResult<IEnumerable<ManufacturingRun>>(_runs.Values);
    }

    public Task<ManufacturingRun> AddAsync(ManufacturingRun run)
    {
        _runs[run.Id] = run;
        return Task.FromResult(run);
    }

    public Task<ManufacturingRun> UpdateAsync(ManufacturingRun run)
    {
        _runs[run.Id] = run;
        return Task.FromResult(run);
    }
}

public class InMemoryMeasurementRepository : IMeasurementRepository
{
    private readonly ConcurrentDictionary<string, MeasurementRecord> _records = new();

    public Task<MeasurementRecord?> GetByIdAsync(string id)
    {
        _records.TryGetValue(id, out var record);
        return Task.FromResult(record);
    }

    public Task<IEnumerable<MeasurementRecord>> GetByRunIdAsync(string runId)
    {
        var records = _records.Values.Where(r => r.ManufacturingRunId == runId);
        return Task.FromResult(records);
    }

    public Task<IEnumerable<MeasurementRecord>> GetByDutIdAsync(string dutId)
    {
        var records = _records.Values.Where(r => r.DutId == dutId);
        return Task.FromResult(records);
    }

    public Task<MeasurementRecord> AddAsync(MeasurementRecord record)
    {
        _records[record.Id] = record;
        return Task.FromResult(record);
    }
}
