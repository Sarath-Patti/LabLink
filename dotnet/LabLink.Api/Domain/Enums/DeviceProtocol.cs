namespace LabLink.Api.Domain.Enums;

/// <summary>
/// Physical or network communication protocol for laboratory equipment.
/// </summary>
public enum DeviceProtocol
{
    SCPI,
    TCP,
    Serial,
    REST,
    Mock
}
