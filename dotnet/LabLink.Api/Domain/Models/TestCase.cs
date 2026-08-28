namespace LabLink.Api.Domain.Models;

/// <summary>
/// Domain entity representing an automated test case specification.
/// </summary>
public class TestCase
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Name { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Suite { get; set; } = "functional";
    public string Category { get; set; } = "optical";
    public bool Enabled { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
