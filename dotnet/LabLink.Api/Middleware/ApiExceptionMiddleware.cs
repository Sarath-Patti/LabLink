using System.Net;
using System.Text.Json;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;

namespace LabLink.Api.Middleware;

public class ApiExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ApiExceptionMiddleware> _logger;

    public ApiExceptionMiddleware(RequestDelegate next, ILogger<ApiExceptionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        HttpStatusCode status;
        string errorCode;
        string message;

        switch (exception)
        {
            case EntityNotFoundException ex:
                status = HttpStatusCode.NotFound;
                errorCode = "entity_not_found";
                message = ex.Message;
                _logger.LogWarning("Entity Not Found: {Message}", message);
                break;

            case ValidationException ex:
                status = HttpStatusCode.BadRequest;
                errorCode = "validation_error";
                message = ex.Message;
                _logger.LogWarning("Validation Error: {Message}", message);
                break;

            case InvalidStateTransitionException ex:
                status = HttpStatusCode.Conflict;
                errorCode = "invalid_state_transition";
                message = ex.Message;
                _logger.LogWarning("Invalid State Transition: {Message}", message);
                break;

            case DuplicateEntityException ex:
                status = HttpStatusCode.Conflict;
                errorCode = "duplicate_entity";
                message = ex.Message;
                _logger.LogWarning("Duplicate Entity: {Message}", message);
                break;

            case DomainException ex:
                status = HttpStatusCode.BadRequest;
                errorCode = "domain_error";
                message = ex.Message;
                _logger.LogWarning("Domain Error: {Message}", message);
                break;

            default:
                status = HttpStatusCode.InternalServerError;
                errorCode = "internal_server_error";
                message = "An unexpected error occurred processing your request.";
                _logger.LogError(exception, "Unhandled Server Error");
                break;
        }

        var response = new ErrorResponse(errorCode, message, DateTime.UtcNow);
        var json = JsonSerializer.Serialize(
            response,
            new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase }
        );

        context.Response.ContentType = "application/json";
        context.Response.StatusCode = (int)status;

        return context.Response.WriteAsync(json);
    }
}
