using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using Microsoft.EntityFrameworkCore;

namespace LabLink.Api.Repositories;

public class PostgresDutRepository : IDutRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresDutRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<Dut?> GetByIdAsync(string id)
    {
        return await _context.Duts.FindAsync(id);
    }

    public async Task<Dut?> GetBySerialNumberAsync(string serialNumber)
    {
        return await _context.Duts.FirstOrDefaultAsync(d => d.SerialNumber == serialNumber);
    }

    public async Task<IEnumerable<Dut>> GetAllAsync()
    {
        return await _context.Duts.ToListAsync();
    }

    public async Task<Dut> AddAsync(Dut dut)
    {
        _context.Duts.Add(dut);
        await _context.SaveChangesAsync();
        return dut;
    }

    public async Task<Dut> UpdateAsync(Dut dut)
    {
        _context.Duts.Update(dut);
        await _context.SaveChangesAsync();
        return dut;
    }
}

public class PostgresManufacturingRunRepository : IManufacturingRunRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresManufacturingRunRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<ManufacturingRun?> GetByIdAsync(string id)
    {
        return await _context.ManufacturingRuns.FindAsync(id);
    }

    public async Task<IEnumerable<ManufacturingRun>> GetByDutIdAsync(string dutId)
    {
        return await _context.ManufacturingRuns.Where(r => r.DutId == dutId).ToListAsync();
    }

    public async Task<IEnumerable<ManufacturingRun>> GetBySerialNumberAsync(string serialNumber)
    {
        return await _context.ManufacturingRuns.Where(r => r.SerialNumber == serialNumber).ToListAsync();
    }

    public async Task<IEnumerable<ManufacturingRun>> GetAllAsync()
    {
        return await _context.ManufacturingRuns.ToListAsync();
    }

    public async Task<ManufacturingRun> AddAsync(ManufacturingRun run)
    {
        _context.ManufacturingRuns.Add(run);
        await _context.SaveChangesAsync();
        return run;
    }

    public async Task<ManufacturingRun> UpdateAsync(ManufacturingRun run)
    {
        _context.ManufacturingRuns.Update(run);
        await _context.SaveChangesAsync();
        return run;
    }
}

public class PostgresMeasurementRepository : IMeasurementRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresMeasurementRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<MeasurementRecord?> GetByIdAsync(string id)
    {
        return await _context.MeasurementRecords.FindAsync(id);
    }

    public async Task<IEnumerable<MeasurementRecord>> GetByRunIdAsync(string runId)
    {
        return await _context.MeasurementRecords.Where(r => r.ManufacturingRunId == runId).ToListAsync();
    }

    public async Task<IEnumerable<MeasurementRecord>> GetByDutIdAsync(string dutId)
    {
        return await _context.MeasurementRecords.Where(r => r.DutId == dutId).ToListAsync();
    }

    public async Task<MeasurementRecord> AddAsync(MeasurementRecord record)
    {
        _context.MeasurementRecords.Add(record);
        await _context.SaveChangesAsync();
        return record;
    }
}
