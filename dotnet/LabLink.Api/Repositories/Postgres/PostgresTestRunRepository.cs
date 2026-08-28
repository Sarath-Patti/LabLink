using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using Microsoft.EntityFrameworkCore;

namespace LabLink.Api.Repositories.Postgres;

public class PostgresTestRunRepository : ITestRunRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresTestRunRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<TestRun>> GetAllAsync()
    {
        return await _context.TestRuns
            .AsNoTracking()
            .OrderByDescending(r => r.StartedAt)
            .ToListAsync();
    }

    public async Task<TestRun?> GetByIdAsync(string id)
    {
        return await _context.TestRuns
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.Id == id);
    }

    public async Task<TestRun> AddAsync(TestRun testRun)
    {
        _context.TestRuns.Add(testRun);
        await _context.SaveChangesAsync();
        return testRun;
    }

    public async Task<TestRun> UpdateAsync(TestRun testRun)
    {
        _context.TestRuns.Update(testRun);
        await _context.SaveChangesAsync();
        return testRun;
    }

    public async Task<bool> DeleteAsync(string id)
    {
        var item = await _context.TestRuns.FindAsync(id);
        if (item == null) return false;

        _context.TestRuns.Remove(item);
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task ClearAsync()
    {
        _context.TestRuns.RemoveRange(_context.TestRuns);
        await _context.SaveChangesAsync();
    }
}
