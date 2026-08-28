using LabLink.Api.Domain.Models;

namespace LabLink.Api.Repositories;

public interface IMeasurementRepository
{
    Task<MeasurementRecord?> GetByIdAsync(string id);
    Task<IEnumerable<MeasurementRecord>> GetByRunIdAsync(string runId);
    Task<IEnumerable<MeasurementRecord>> GetByDutIdAsync(string dutId);
    Task<MeasurementRecord> AddAsync(MeasurementRecord record);
}
