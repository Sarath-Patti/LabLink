using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using Microsoft.EntityFrameworkCore;

namespace LabLink.Api.Repositories.Postgres;

public class PostgresInstrumentRepository : IInstrumentRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresInstrumentRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<Instrument>> GetAllAsync()
    {
        return await _context.Instruments
            .AsNoTracking()
            .OrderBy(i => i.Name)
            .ToListAsync();
    }

    public async Task<Instrument?> GetByIdAsync(string id)
    {
        return await _context.Instruments
            .AsNoTracking()
            .FirstOrDefaultAsync(i => i.Id == id);
    }

    public async Task<Instrument> AddAsync(Instrument instrument)
    {
        _context.Instruments.Add(instrument);
        await _context.SaveChangesAsync();
        return instrument;
    }

    public async Task<Instrument> UpdateAsync(Instrument instrument)
    {
        _context.Instruments.Update(instrument);
        await _context.SaveChangesAsync();
        return instrument;
    }

    public async Task<bool> DeleteAsync(string id)
    {
        var item = await _context.Instruments.FindAsync(id);
        if (item == null) return false;

        _context.Instruments.Remove(item);
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task ClearAsync()
    {
        _context.Instruments.RemoveRange(_context.Instruments);
        await _context.SaveChangesAsync();
    }
}
