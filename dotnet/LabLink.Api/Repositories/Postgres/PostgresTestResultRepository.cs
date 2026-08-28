using LabLink.Api.Domain.Models;
using LabLink.Api.Persistence;
using Microsoft.EntityFrameworkCore;

namespace LabLink.Api.Repositories.Postgres;

public class PostgresTestResultRepository : ITestResultRepository
{
    private readonly LabLinkDbContext _context;

    public PostgresTestResultRepository(LabLinkDbContext context)
    {
        _context = context;
    }

    public async Task<IEnumerable<TestResult>> GetByTestRunIdAsync(string testRunId)
    {
        return await _context.TestResults
            .AsNoTracking()
            .Where(r => r.TestRunId == testRunId)
            .OrderBy(r => r.Timestamp)
            .ToListAsync();
    }

    public async Task<TestResult?> GetByIdAsync(string id)
    {
        return await _context.TestResults
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.Id == id);
    }

    public async Task<TestResult> AddAsync(TestResult testResult)
    {
        _context.TestResults.Add(testResult);
        await _context.SaveChangesAsync();
        return testResult;
    }

    public async Task ClearAsync()
    {
        _context.TestResults.RemoveRange(_context.TestResults);
        await _context.SaveChangesAsync();
    }
}
