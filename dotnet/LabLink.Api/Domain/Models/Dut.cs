using LabLink.Api.Domain.Enums;

namespace LabLink.Api.Domain.Models;

public class Dut
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string SerialNumber { get; set; } = string.Empty;
    public string PartNumber { get; set; } = string.Empty;
    public string HardwareRevision { get; set; } = string.Empty;
    public string FirmwareVersion { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DutStatus Status { get; set; } = DutStatus.Untested;
}
