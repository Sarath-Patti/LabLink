using LabLink.Api.Domain.Enums;
using LabLink.Api.Domain.Models;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;
using LabLink.Api.Repositories;

namespace LabLink.Api.Services;

public class DutService
{
    private readonly IDutRepository _dutRepository;
    private readonly ILogger<DutService> _logger;

    public DutService(IDutRepository dutRepository, ILogger<DutService> logger)
    {
        _dutRepository = dutRepository;
        _logger = logger;
    }

    public async Task<DutDto> RegisterDutAsync(CreateDutRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.SerialNumber))
        {
            throw new ValidationException("Serial number is required.");
        }

        var existing = await _dutRepository.GetBySerialNumberAsync(request.SerialNumber.Trim());
        if (existing != null)
        {
            throw new DuplicateEntityException("DUT", request.SerialNumber.Trim());
        }

        var dut = new Dut
        {
            SerialNumber = request.SerialNumber.Trim(),
            PartNumber = request.PartNumber?.Trim() ?? string.Empty,
            HardwareRevision = request.HardwareRevision?.Trim() ?? string.Empty,
            FirmwareVersion = request.FirmwareVersion?.Trim() ?? string.Empty,
            CreatedAt = DateTime.UtcNow,
            Status = DutStatus.Untested
        };

        var saved = await _dutRepository.AddAsync(dut);
        _logger.LogInformation("Registered new DUT '{SerialNumber}' [ID: {Id}]", saved.SerialNumber, saved.Id);

        return MapToDto(saved);
    }

    public async Task<DutDto> GetDutByIdAsync(string id)
    {
        var dut = await _dutRepository.GetByIdAsync(id);
        if (dut == null)
        {
            throw new EntityNotFoundException("DUT", id);
        }
        return MapToDto(dut);
    }

    public async Task<DutDto> GetDutBySerialNumberAsync(string serialNumber)
    {
        var dut = await _dutRepository.GetBySerialNumberAsync(serialNumber.Trim());
        if (dut == null)
        {
            throw new EntityNotFoundException("DUT", serialNumber.Trim());
        }
        return MapToDto(dut);
    }

    public async Task<IEnumerable<DutDto>> GetAllDutsAsync()
    {
        var duts = await _dutRepository.GetAllAsync();
        return duts.Select(MapToDto);
    }

    public static DutDto MapToDto(Dut dut) => new(
        dut.Id,
        dut.SerialNumber,
        dut.PartNumber,
        dut.HardwareRevision,
        dut.FirmwareVersion,
        dut.CreatedAt,
        dut.Status.ToString()
    );
}
