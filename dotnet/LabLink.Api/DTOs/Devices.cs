using System.ComponentModel.DataAnnotations;
using LabLink.Api.Domain.Enums;

namespace LabLink.Api.DTOs;

public record CreateDeviceRequest(
    [Required] string Name,
    [Required] DeviceType Type,
    string Model = "",
    [Required] string Address = "",
    DeviceProtocol Protocol = DeviceProtocol.TCP,
    bool Enabled = true,
    Dictionary<string, string>? Metadata = null
);

public record DeviceResponse(
    string Id,
    string Name,
    string Type,
    string Model,
    string Address,
    string Protocol,
    bool Enabled,
    Dictionary<string, string> Metadata
);
