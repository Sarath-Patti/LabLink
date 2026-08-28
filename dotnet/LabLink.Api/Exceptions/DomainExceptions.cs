namespace LabLink.Api.Exceptions;

public class DomainException : Exception
{
    public DomainException(string message) : base(message) { }
}

public class EntityNotFoundException : DomainException
{
    public EntityNotFoundException(string entityName, string id)
        : base($"{entityName} with ID '{id}' was not found.") { }
}

public class ValidationException : DomainException
{
    public ValidationException(string message) : base(message) { }
}

public class InvalidStateTransitionException : DomainException
{
    public InvalidStateTransitionException(string currentStatus, string targetStatus)
        : base($"Cannot transition test run status from '{currentStatus}' to '{targetStatus}'.") { }
}

public class DuplicateEntityException : DomainException
{
    public DuplicateEntityException(string entityName, string identifier)
        : base($"{entityName} with identifier '{identifier}' already exists.") { }
}
