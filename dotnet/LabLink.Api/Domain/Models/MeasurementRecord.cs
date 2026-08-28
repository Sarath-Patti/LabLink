using LabLink.Api.Domain.Enums;

namespace LabLink.Api.Domain.Models;

public class MeasurementRecord
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string ManufacturingRunId { get; set; } = string.Empty;
    public string DutId { get; set; } = string.Empty;
    public string StepName { get; set; } = string.Empty;
    public string MeasurementName { get; set; } = string.Empty;
    public double Value { get; set; }
    public string Unit { get; set; } = string.Empty;
    public double? LowerLimit { get; set; }
    public double? UpperLimit { get; set; }
    public string? ExpectedValue { get; set; }
    public TestStatus Verdict { get; set; } = TestStatus.Passed;
    public FailureCode FailureCode { get; set; } = FailureCode.NONE;
    public string InstrumentSource { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}
