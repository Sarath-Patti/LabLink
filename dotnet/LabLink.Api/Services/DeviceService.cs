using LabLink.Api.Domain.Models;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;
using LabLink.Api.Repositories;

namespace LabLink.Api.Services;

public class DeviceService
{
    private readonly IDeviceRepository _repository;
    private readonly ILogger<DeviceService> _logger;

    public DeviceService(IDeviceRepository repository, ILogger<DeviceService> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    public async Task<IEnumerable<DeviceResponse>> GetAllAsync()
    {
        var devices = await _repository.GetAllAsync();
        return devices.Select(ToResponse);
    }

    public async Task<DeviceResponse> GetByIdAsync(string id)
    {
        var device = await _repository.GetByIdAsync(id);
        if (device == null)
        {
            throw new EntityNotFoundException(nameof(Device), id);
        }
        return ToResponse(device);
    }

    public async Task<DeviceResponse> CreateAsync(CreateDeviceRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Name))
        {
            throw new ValidationException("Device name cannot be empty.");
        }

        if (string.IsNullOrWhiteSpace(request.Address))
        {
            throw new ValidationException("Device address cannot be empty.");
        }

        var device = new Device
        {
            Name = request.Name.Trim(),
            Type = request.Type,
            Model = request.Model.Trim(),
            Address = request.Address.Trim(),
            Protocol = request.Protocol,
            Enabled = request.Enabled,
            Metadata = request.Metadata ?? new Dictionary<string, string>()
        };

        var created = await _repository.AddAsync(device);
        _logger.LogInformation(
            "Registered new device '{Name}' [Type: {Type}, Address: {Address}]",
            created.Name,
            created.Type,
            created.Address
        );

        return ToResponse(created);
    }

    private static DeviceResponse ToResponse(Device d) =>
        new(
            d.Id,
            d.Name,
            d.Type.ToString(),
            d.Model,
            d.Address,
            d.Protocol.ToString(),
            d.Enabled,
            d.Metadata
        );
}
