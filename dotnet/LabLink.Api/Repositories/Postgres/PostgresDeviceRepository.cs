using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using Microsoft.EntityFrameworkCore;

namespace LabLink.Api.Repositories.Postgres;

public class PostgresDeviceRepository : IDeviceRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresDeviceRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<Device>> GetAllAsync()
    {
        return await _context.Devices
            .AsNoTracking()
            .OrderBy(d => d.Name)
            .ToListAsync();
    }

    public async Task<Device?> GetByIdAsync(string id)
    {
        return await _context.Devices
            .AsNoTracking()
            .FirstOrDefaultAsync(d => d.Id == id);
    }

    public async Task<Device> AddAsync(Device device)
    {
        _context.Devices.Add(device);
        await _context.SaveChangesAsync();
        return device;
    }

    public async Task<Device> UpdateAsync(Device device)
    {
        _context.Devices.Update(device);
        await _context.SaveChangesAsync();
        return device;
    }

    public async Task<bool> DeleteAsync(string id)
    {
        var item = await _context.Devices.FindAsync(id);
        if (item == null) return false;

        _context.Devices.Remove(item);
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task ClearAsync()
    {
        _context.Devices.RemoveRange(_context.Devices);
        await _context.SaveChangesAsync();
    }
}
