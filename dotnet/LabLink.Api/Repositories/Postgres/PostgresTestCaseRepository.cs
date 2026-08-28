using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using Microsoft.EntityFrameworkCore;

namespace LabLink.Api.Repositories.Postgres;

public class PostgresTestCaseRepository : ITestCaseRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresTestCaseRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<TestCase>> GetAllAsync()
    {
        return await _context.TestCases
            .AsNoTracking()
            .OrderByDescending(t => t.CreatedAt)
            .ToListAsync();
    }

    public async Task<TestCase?> GetByIdAsync(string id)
    {
        return await _context.TestCases
            .AsNoTracking()
            .FirstOrDefaultAsync(t => t.Id == id);
    }

    public async Task<TestCase> AddAsync(TestCase testCase)
    {
        _context.TestCases.Add(testCase);
        await _context.SaveChangesAsync();
        return testCase;
    }

    public async Task<TestCase> UpdateAsync(TestCase testCase)
    {
        _context.TestCases.Update(testCase);
        await _context.SaveChangesAsync();
        return testCase;
    }

    public async Task<bool> DeleteAsync(string id)
    {
        var item = await _context.TestCases.FindAsync(id);
        if (item == null) return false;

        _context.TestCases.Remove(item);
        await _context.SaveChangesAsync();
        return true;
    }

    public async Task ClearAsync()
    {
        _context.TestCases.RemoveRange(_context.TestCases);
        await _context.SaveChangesAsync();
    }
}
