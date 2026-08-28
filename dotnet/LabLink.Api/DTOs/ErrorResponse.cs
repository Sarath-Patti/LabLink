namespace LabLink.Api.DTOs;

/// <summary>
/// Structured error payload for REST API error responses.
/// </summary>
public record ErrorResponse(
    string Error,
    string Message,
    DateTime Timestamp
);
