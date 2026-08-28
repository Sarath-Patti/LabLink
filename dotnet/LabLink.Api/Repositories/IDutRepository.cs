using LabLink.Api.Domain.Models;

namespace LabLink.Api.Repositories;

public interface IDutRepository
{
    Task<Dut?> GetByIdAsync(string id);
    Task<Dut?> GetBySerialNumberAsync(string serialNumber);
    Task<IEnumerable<Dut>> GetAllAsync();
    Task<Dut> AddAsync(Dut dut);
    Task<Dut> UpdateAsync(Dut dut);
}
