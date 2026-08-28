using LabLink.Api.Domain.Enums;
using LabLink.Api.Domain.Models;
using LabLink.Api.DTOs;
using LabLink.Api.Exceptions;
using LabLink.Api.Repositories;

namespace LabLink.Api.Services;

public class ManufacturingService
{
    private readonly IDutRepository _dutRepository;
    private readonly IManufacturingRunRepository _runRepository;
    private readonly IMeasurementRepository _measurementRepository;
    private readonly ILogger<ManufacturingService> _logger;

    public ManufacturingService(
        IDutRepository dutRepository,
        IManufacturingRunRepository runRepository,
        IMeasurementRepository measurementRepository,
        ILogger<ManufacturingService> logger)
    {
        _dutRepository = dutRepository;
        _runRepository = runRepository;
        _measurementRepository = measurementRepository;
        _logger = logger;
    }

    public async Task<ManufacturingRunDto> CreateRunAsync(CreateManufacturingRunRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.SerialNumber))
        {
            throw new ValidationException("Serial number is required.");
        }

        var dut = await _dutRepository.GetBySerialNumberAsync(request.SerialNumber.Trim());
        if (dut == null)
        {
            // Auto-register DUT if not present for seamless simulation
            dut = await _dutRepository.AddAsync(new Dut
            {
                SerialNumber = request.SerialNumber.Trim(),
                Status = DutStatus.Untested
            });
        }

        var previousRuns = await _runRepository.GetByDutIdAsync(dut.Id);
        var isFirstPass = !previousRuns.Any();

        var run = new ManufacturingRun
        {
            DutId = dut.Id,
            SerialNumber = dut.SerialNumber,
            StationId = request.StationId?.Trim() ?? "Station-01",
            SequenceName = request.SequenceName?.Trim() ?? "DefaultSequence",
            SequenceVersion = request.SequenceVersion?.Trim() ?? "1.0",
            SoftwareVersion = request.SoftwareVersion?.Trim() ?? "1.0.0",
            StartedAt = DateTime.UtcNow,
            Verdict = TestRunStatus.Running,
            FirstPass = isFirstPass,
            FailureCode = FailureCode.NONE
        };

        var saved = await _runRepository.AddAsync(run);
        _logger.LogInformation("Created ManufacturingRun '{Id}' for DUT '{SerialNumber}' (FirstPass: {FirstPass})", saved.Id, saved.SerialNumber, isFirstPass);

        return MapToDto(saved);
    }

    public async Task<ManufacturingRunDto> GetRunByIdAsync(string id)
    {
        var run = await _runRepository.GetByIdAsync(id);
        if (run == null)
        {
            throw new EntityNotFoundException("ManufacturingRun", id);
        }
        return MapToDto(run);
    }

    public async Task<MeasurementRecordDto> AddMeasurementAsync(string runId, AddMeasurementRequest request)
    {
        var run = await _runRepository.GetByIdAsync(runId);
        if (run == null)
        {
            throw new EntityNotFoundException("ManufacturingRun", runId);
        }

        if (run.Verdict == TestRunStatus.Completed || run.Verdict == TestRunStatus.Cancelled)
        {
            throw new InvalidStateTransitionException(run.Verdict.ToString(), "MeasurementIngestion");
        }

        Enum.TryParse<TestStatus>(request.Verdict, true, out var verdictEnum);
        Enum.TryParse<FailureCode>(request.FailureCode, true, out var codeEnum);

        var record = new MeasurementRecord
        {
            ManufacturingRunId = runId,
            DutId = run.DutId,
            StepName = request.StepName?.Trim() ?? string.Empty,
            MeasurementName = request.MeasurementName?.Trim() ?? string.Empty,
            Value = request.Value,
            Unit = request.Unit?.Trim() ?? string.Empty,
            LowerLimit = request.LowerLimit,
            UpperLimit = request.UpperLimit,
            ExpectedValue = request.ExpectedValue?.Trim(),
            Verdict = verdictEnum,
            FailureCode = codeEnum,
            InstrumentSource = request.InstrumentSource?.Trim() ?? string.Empty,
            Timestamp = DateTime.UtcNow
        };

        var saved = await _measurementRepository.AddAsync(record);
        _logger.LogInformation("Added measurement '{Name}'={Value} {Unit} (Verdict: {Verdict}) to run '{RunId}'", saved.MeasurementName, saved.Value, saved.Unit, saved.Verdict, runId);

        return MapToMeasurementDto(saved);
    }

    public async Task<ManufacturingRunDto> CompleteRunAsync(string runId, CompleteManufacturingRunRequest request)
    {
        var run = await _runRepository.GetByIdAsync(runId);
        if (run == null)
        {
            throw new EntityNotFoundException("ManufacturingRun", runId);
        }

        Enum.TryParse<TestRunStatus>(request.Verdict, true, out var verdictEnum);
        if (verdictEnum == TestRunStatus.Created)
        {
            verdictEnum = TestRunStatus.Completed;
        }

        Enum.TryParse<FailureCode>(request.FailureCode, true, out var codeEnum);

        run.CompletedAt = DateTime.UtcNow;
        run.DurationSeconds = Math.Round((run.CompletedAt.Value - run.StartedAt).TotalSeconds, 3);
        run.Verdict = verdictEnum;
        run.FailureCode = codeEnum;
        run.FailureSummary = request.FailureSummary;

        var updated = await _runRepository.UpdateAsync(run);

        // Update DUT overall status
        var dut = await _dutRepository.GetByIdAsync(run.DutId);
        if (dut != null)
        {
            dut.Status = (verdictEnum == TestRunStatus.Completed && codeEnum == FailureCode.NONE)
                ? DutStatus.Passed
                : DutStatus.Failed;
            await _dutRepository.UpdateAsync(dut);
        }

        _logger.LogInformation("Completed ManufacturingRun '{Id}' -> Verdict: {Verdict}, FailureCode: {FailureCode}", updated.Id, updated.Verdict, updated.FailureCode);
        return MapToDto(updated);
    }

    public async Task<IEnumerable<MeasurementRecordDto>> GetRunMeasurementsAsync(string runId)
    {
        var records = await _measurementRepository.GetByRunIdAsync(runId);
        return records.Select(MapToMeasurementDto);
    }

    public async Task<YieldAnalyticsDto> GetYieldAnalyticsAsync()
    {
        var runs = (await _runRepository.GetAllAsync()).ToList();

        var finishedRuns = runs.Where(r => r.Verdict != TestRunStatus.Running && r.Verdict != TestRunStatus.Created).ToList();
        var firstPassRuns = finishedRuns.Where(r => r.FirstPass).ToList();
        var totalFirstPass = firstPassRuns.Count;
        var firstPassPassed = firstPassRuns.Count(r => r.Verdict == TestRunStatus.Completed && r.FailureCode == FailureCode.NONE);
        var fpyPercentage = totalFirstPass > 0 ? Math.Round((double)firstPassPassed / totalFirstPass * 100.0, 2) : 0.0;

        var dutGrouped = runs.GroupBy(r => r.DutId);
        var totalDutsTested = dutGrouped.Count();
        var finalPassedDuts = dutGrouped.Count(g => g.Any(r => r.Verdict == TestRunStatus.Completed && r.FailureCode == FailureCode.NONE));
        var finalYieldPercentage = totalDutsTested > 0 ? Math.Round((double)finalPassedDuts / totalDutsTested * 100.0, 2) : 0.0;

        var failuresByCode = runs
            .Where(r => r.FailureCode != FailureCode.NONE)
            .GroupBy(r => r.FailureCode.ToString())
            .ToDictionary(g => g.Key, g => g.Count());

        var failuresByStation = runs
            .Where(r => r.FailureCode != FailureCode.NONE || r.Verdict == TestRunStatus.Cancelled)
            .GroupBy(r => string.IsNullOrWhiteSpace(r.StationId) ? "Unknown" : r.StationId)
            .ToDictionary(g => g.Key, g => g.Count());

        var allMeasurements = new List<MeasurementRecord>();
        foreach (var run in runs)
        {
            var m = await _measurementRepository.GetByRunIdAsync(run.Id);
            allMeasurements.AddRange(m);
        }

        var failuresByStep = allMeasurements
            .Where(m => m.Verdict == TestStatus.Failed || m.Verdict == TestStatus.Error)
            .GroupBy(m => string.IsNullOrWhiteSpace(m.StepName) ? "Unknown" : m.StepName)
            .ToDictionary(g => g.Key, g => g.Count());

        return new YieldAnalyticsDto(
            totalDutsTested,
            firstPassPassed,
            fpyPercentage,
            finalPassedDuts,
            finalYieldPercentage,
            failuresByStep,
            failuresByCode,
            failuresByStation
        );
    }

    public static ManufacturingRunDto MapToDto(ManufacturingRun r) => new(
        r.Id,
        r.DutId,
        r.SerialNumber,
        r.StationId,
        r.SequenceName,
        r.SequenceVersion,
        r.SoftwareVersion,
        r.StartedAt,
        r.CompletedAt,
        r.DurationSeconds,
        r.Verdict.ToString(),
        r.FirstPass,
        r.FailureCode.ToString(),
        r.FailureSummary
    );

    public static MeasurementRecordDto MapToMeasurementDto(MeasurementRecord m) => new(
        m.Id,
        m.ManufacturingRunId,
        m.DutId,
        m.StepName,
        m.MeasurementName,
        m.Value,
        m.Unit,
        m.LowerLimit,
        m.UpperLimit,
        m.ExpectedValue,
        m.Verdict.ToString(),
        m.FailureCode.ToString(),
        m.InstrumentSource,
        m.Timestamp
    );
}
