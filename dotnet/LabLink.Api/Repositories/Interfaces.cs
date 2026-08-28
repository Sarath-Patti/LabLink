using LabLink.Api.Domain.Models;

namespace LabLink.Api.Repositories;

public interface ITestCaseRepository
{
    Task<IEnumerable<TestCase>> GetAllAsync();
    Task<TestCase?> GetByIdAsync(string id);
    Task<TestCase> AddAsync(TestCase testCase);
    Task<TestCase> UpdateAsync(TestCase testCase);
    Task<bool> DeleteAsync(string id);
    Task ClearAsync();
}

public interface ITestRunRepository
{
    Task<IEnumerable<TestRun>> GetAllAsync();
    Task<TestRun?> GetByIdAsync(string id);
    Task<TestRun> AddAsync(TestRun testRun);
    Task<TestRun> UpdateAsync(TestRun testRun);
    Task<bool> DeleteAsync(string id);
    Task ClearAsync();
}

public interface ITestResultRepository
{
    Task<IEnumerable<TestResult>> GetByTestRunIdAsync(string testRunId);
    Task<TestResult?> GetByIdAsync(string id);
    Task<TestResult> AddAsync(TestResult testResult);
    Task ClearAsync();
}

public interface IDeviceRepository
{
    Task<IEnumerable<Device>> GetAllAsync();
    Task<Device?> GetByIdAsync(string id);
    Task<Device> AddAsync(Device device);
    Task<Device> UpdateAsync(Device device);
    Task<bool> DeleteAsync(string id);
    Task ClearAsync();
}

public interface IInstrumentRepository
{
    Task<IEnumerable<Instrument>> GetAllAsync();
    Task<Instrument?> GetByIdAsync(string id);
    Task<Instrument> AddAsync(Instrument instrument);
    Task<Instrument> UpdateAsync(Instrument instrument);
    Task<bool> DeleteAsync(string id);
    Task ClearAsync();
}
