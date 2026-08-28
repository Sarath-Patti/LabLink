using LabLink.Api.Domain.Models;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;
using LabLink.Api.Repositories;

namespace LabLink.Api.Services;

public class InstrumentService
{
    private readonly IInstrumentRepository _repository;
    private readonly ILogger<InstrumentService> _logger;

    public InstrumentService(IInstrumentRepository repository, ILogger<InstrumentService> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    public async Task<IEnumerable<InstrumentResponse>> GetAllAsync()
    {
        var instruments = await _repository.GetAllAsync();
        return instruments.Select(ToResponse);
    }

    public async Task<InstrumentResponse> GetByIdAsync(string id)
    {
        var instrument = await _repository.GetByIdAsync(id);
        if (instrument == null)
        {
            throw new EntityNotFoundException(nameof(Instrument), id);
        }
        return ToResponse(instrument);
    }

    public async Task<InstrumentResponse> CreateAsync(CreateInstrumentRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Name))
        {
            throw new ValidationException("Instrument name cannot be empty.");
        }

        if (string.IsNullOrWhiteSpace(request.Type))
        {
            throw new ValidationException("Instrument type cannot be empty.");
        }

        if (string.IsNullOrWhiteSpace(request.Address))
        {
            throw new ValidationException("Instrument address cannot be empty.");
        }

        var instrument = new Instrument
        {
            Name = request.Name.Trim(),
            Type = request.Type.Trim(),
            Model = request.Model.Trim(),
            Interface = string.IsNullOrWhiteSpace(request.Interface) ? "TCPIP" : request.Interface.Trim(),
            Address = request.Address.Trim(),
            Enabled = request.Enabled
        };

        var created = await _repository.AddAsync(instrument);
        _logger.LogInformation(
            "Registered new instrument '{Name}' [Type: {Type}, Interface: {Interface}, Address: {Address}]",
            created.Name,
            created.Type,
            created.Interface,
            created.Address
        );

        return ToResponse(created);
    }

    private static InstrumentResponse ToResponse(Instrument i) =>
        new(
            i.Id,
            i.Name,
            i.Type,
            i.Model,
            i.Interface,
            i.Address,
            i.Enabled
        );
}
