using LabLink.Api.Domain.Enums;

namespace LabLink.Api.DTOs;

public record DutDto(
    string Id,
    string SerialNumber,
    string PartNumber,
    string HardwareRevision,
    string FirmwareVersion,
    DateTime CreatedAt,
    string Status
);

public record CreateDutRequest(
    string SerialNumber,
    string PartNumber,
    string HardwareRevision,
    string FirmwareVersion
);

public record ManufacturingRunDto(
    string Id,
    string DutId,
    string SerialNumber,
    string StationId,
    string SequenceName,
    string SequenceVersion,
    string SoftwareVersion,
    DateTime StartedAt,
    DateTime? CompletedAt,
    double DurationSeconds,
    string Verdict,
    bool FirstPass,
    string FailureCode,
    string? FailureSummary
);

public record CreateManufacturingRunRequest(
    string SerialNumber,
    string StationId,
    string SequenceName,
    string SequenceVersion,
    string SoftwareVersion
);

public record MeasurementRecordDto(
    string Id,
    string ManufacturingRunId,
    string DutId,
    string StepName,
    string MeasurementName,
    double Value,
    string Unit,
    double? LowerLimit,
    double? UpperLimit,
    string? ExpectedValue,
    string Verdict,
    string FailureCode,
    string InstrumentSource,
    DateTime Timestamp
);

public record AddMeasurementRequest(
    string StepName,
    string MeasurementName,
    double Value,
    string Unit,
    double? LowerLimit,
    double? UpperLimit,
    string? ExpectedValue,
    string Verdict,
    string FailureCode,
    string InstrumentSource
);

public record CompleteManufacturingRunRequest(
    string Verdict,
    string FailureCode,
    string? FailureSummary
);

public record YieldAnalyticsDto(
    int TotalUnitsTested,
    int FirstPassPassed,
    double FirstPassYieldPercentage,
    int FinalPassed,
    double FinalYieldPercentage,
    Dictionary<string, int> FailuresByStep,
    Dictionary<string, int> FailuresByCode,
    Dictionary<string, int> FailuresByStation
);
