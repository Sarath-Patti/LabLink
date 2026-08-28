using LabLink.Api.Domain.Enums;

namespace LabLink.Api.Domain.Models;

/// <summary>
/// Domain entity representing a test network target device or system under test.
/// </summary>
public class Device
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public DeviceType Type { get; set; } = DeviceType.GenericDevice;
    public string Model { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;
    public DeviceProtocol Protocol { get; set; } = DeviceProtocol.TCP;
    public bool Enabled { get; set; } = true;
    public Dictionary<string, string> Metadata { get; set; } = new();
}
