using LabLink.Api.Domain.Models;

namespace LabLink.Api.Repositories;

public interface IManufacturingRunRepository
{
    Task<ManufacturingRun?> GetByIdAsync(string id);
    Task<IEnumerable<ManufacturingRun>> GetByDutIdAsync(string dutId);
    Task<IEnumerable<ManufacturingRun>> GetBySerialNumberAsync(string serialNumber);
    Task<IEnumerable<ManufacturingRun>> GetAllAsync();
    Task<ManufacturingRun> AddAsync(ManufacturingRun run);
    Task<ManufacturingRun> UpdateAsync(ManufacturingRun run);
}
