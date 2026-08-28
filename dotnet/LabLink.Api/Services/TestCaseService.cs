using LabLink.Api.Domain.Models;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;
using LabLink.Api.Repositories;

namespace LabLink.Api.Services;

public class TestCaseService
{
    private readonly ITestCaseRepository _repository;
    private readonly ILogger<TestCaseService> _logger;

    public TestCaseService(ITestCaseRepository repository, ILogger<TestCaseService> logger)
    {
        _repository = repository;
        _logger = logger;
    }

    public async Task<IEnumerable<TestCaseResponse>> GetAllAsync()
    {
        var items = await _repository.GetAllAsync();
        return items.Select(ToResponse);
    }

    public async Task<TestCaseResponse> GetByIdAsync(string id)
    {
        var item = await _repository.GetByIdAsync(id);
        if (item == null)
        {
            throw new EntityNotFoundException(nameof(TestCase), id);
        }
        return ToResponse(item);
    }

    public async Task<TestCaseResponse> CreateAsync(CreateTestCaseRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Name))
        {
            throw new ValidationException("Test case name cannot be empty.");
        }

        var entity = new TestCase
        {
            Name = request.Name.Trim(),
            Description = request.Description.Trim(),
            Suite = string.IsNullOrWhiteSpace(request.Suite) ? "functional" : request.Suite.Trim(),
            Category = string.IsNullOrWhiteSpace(request.Category) ? "optical" : request.Category.Trim(),
            Enabled = request.Enabled,
            CreatedAt = DateTime.UtcNow
        };

        var created = await _repository.AddAsync(entity);
        _logger.LogInformation("Created new test case '{Name}' [ID: {Id}]", created.Name, created.Id);
        return ToResponse(created);
    }

    private static TestCaseResponse ToResponse(TestCase tc) =>
        new(tc.Id, tc.Name, tc.Description, tc.Suite, tc.Category, tc.Enabled, tc.CreatedAt);
}
