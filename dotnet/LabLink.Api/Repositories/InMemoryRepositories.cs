using System.Collections.Concurrent;
using LabLink.Api.Domain.Models;

namespace LabLink.Api.Repositories;

public class InMemoryTestCaseRepository : ITestCaseRepository
{
    private readonly ConcurrentDictionary<string, TestCase> _storage = new();

    public Task<IEnumerable<TestCase>> GetAllAsync() =>
        Task.FromResult<IEnumerable<TestCase>>(_storage.Values.OrderByDescending(t => t.CreatedAt));

    public Task<TestCase?> GetByIdAsync(string id) =>
        Task.FromResult(_storage.TryGetValue(id, out var item) ? item : null);

    public Task<TestCase> AddAsync(TestCase testCase)
    {
        _storage[testCase.Id] = testCase;
        return Task.FromResult(testCase);
    }

    public Task<TestCase> UpdateAsync(TestCase testCase)
    {
        _storage[testCase.Id] = testCase;
        return Task.FromResult(testCase);
    }

    public Task<bool> DeleteAsync(string id) =>
        Task.FromResult(_storage.TryRemove(id, out _));

    public Task ClearAsync()
    {
        _storage.Clear();
        return Task.CompletedTask;
    }
}

public class InMemoryTestRunRepository : ITestRunRepository
{
    private readonly ConcurrentDictionary<string, TestRun> _storage = new();

    public Task<IEnumerable<TestRun>> GetAllAsync() =>
        Task.FromResult<IEnumerable<TestRun>>(_storage.Values.OrderByDescending(r => r.StartedAt));

    public Task<TestRun?> GetByIdAsync(string id) =>
        Task.FromResult(_storage.TryGetValue(id, out var item) ? item : null);

    public Task<TestRun> AddAsync(TestRun testRun)
    {
        _storage[testRun.Id] = testRun;
        return Task.FromResult(testRun);
    }

    public Task<TestRun> UpdateAsync(TestRun testRun)
    {
        _storage[testRun.Id] = testRun;
        return Task.FromResult(testRun);
    }

    public Task<bool> DeleteAsync(string id) =>
        Task.FromResult(_storage.TryRemove(id, out _));

    public Task ClearAsync()
    {
        _storage.Clear();
        return Task.CompletedTask;
    }
}

public class InMemoryTestResultRepository : ITestResultRepository
{
    private readonly ConcurrentDictionary<string, TestResult> _storage = new();

    public Task<IEnumerable<TestResult>> GetByTestRunIdAsync(string testRunId) =>
        Task.FromResult<IEnumerable<TestResult>>(
            _storage.Values.Where(r => r.TestRunId == testRunId).OrderBy(r => r.Timestamp)
        );

    public Task<TestResult?> GetByIdAsync(string id) =>
        Task.FromResult(_storage.TryGetValue(id, out var item) ? item : null);

    public Task<TestResult> AddAsync(TestResult testResult)
    {
        _storage[testResult.Id] = testResult;
        return Task.FromResult(testResult);
    }

    public Task ClearAsync()
    {
        _storage.Clear();
        return Task.CompletedTask;
    }
}

public class InMemoryDeviceRepository : IDeviceRepository
{
    private readonly ConcurrentDictionary<string, Device> _storage = new();

    public Task<IEnumerable<Device>> GetAllAsync() =>
        Task.FromResult<IEnumerable<Device>>(_storage.Values.OrderBy(d => d.Name));

    public Task<Device?> GetByIdAsync(string id) =>
        Task.FromResult(_storage.TryGetValue(id, out var item) ? item : null);

    public Task<Device> AddAsync(Device device)
    {
        _storage[device.Id] = device;
        return Task.FromResult(device);
    }

    public Task<Device> UpdateAsync(Device device)
    {
        _storage[device.Id] = device;
        return Task.FromResult(device);
    }

    public Task<bool> DeleteAsync(string id) =>
        Task.FromResult(_storage.TryRemove(id, out _));

    public Task ClearAsync()
    {
        _storage.Clear();
        return Task.CompletedTask;
    }
}

public class InMemoryInstrumentRepository : IInstrumentRepository
{
    private readonly ConcurrentDictionary<string, Instrument> _storage = new();

    public Task<IEnumerable<Instrument>> GetAllAsync() =>
        Task.FromResult<IEnumerable<Instrument>>(_storage.Values.OrderBy(i => i.Name));

    public Task<Instrument?> GetByIdAsync(string id) =>
        Task.FromResult(_storage.TryGetValue(id, out var item) ? item : null);

    public Task<Instrument> AddAsync(Instrument instrument)
    {
        _storage[instrument.Id] = instrument;
        return Task.FromResult(instrument);
    }

    public Task<Instrument> UpdateAsync(Instrument instrument)
    {
        _storage[instrument.Id] = instrument;
        return Task.FromResult(instrument);
    }

    public Task<bool> DeleteAsync(string id) =>
        Task.FromResult(_storage.TryRemove(id, out _));

    public Task ClearAsync()
    {
        _storage.Clear();
        return Task.CompletedTask;
    }
}
