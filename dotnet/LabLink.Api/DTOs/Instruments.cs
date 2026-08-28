using System.ComponentModel.DataAnnotations;

namespace LabLink.Api.DTOs;

public record CreateInstrumentRequest(
    [Required] string Name,
    [Required] string Type,
    string Model = "",
    string Interface = "TCPIP",
    [Required] string Address = "",
    bool Enabled = true
);

public record InstrumentResponse(
    string Id,
    string Name,
    string Type,
    string Model,
    string Interface,
    string Address,
    bool Enabled
);
