using System.ComponentModel.DataAnnotations;

namespace LabLink.Api.DTOs;

public record CreateTestCaseRequest(
    [Required] string Name,
    string Description = "",
    string Suite = "functional",
    string Category = "optical",
    bool Enabled = true
);

public record TestCaseResponse(
    string Id,
    string Name,
    string Description,
    string Suite,
    string Category,
    bool Enabled,
    DateTime CreatedAt
);
