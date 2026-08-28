namespace LabLink.Api.Domain.Models;

/// <summary>
/// Domain entity representing a test laboratory instrument driver metadata object.
/// </summary>
public class Instrument
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public string Interface { get; set; } = "TCPIP";
    public string Address { get; set; } = string.Empty;
    public bool Enabled { get; set; } = true;
}
