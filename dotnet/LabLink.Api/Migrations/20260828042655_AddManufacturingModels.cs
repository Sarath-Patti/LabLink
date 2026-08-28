using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace LabLink.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddManufacturingModels : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Duts",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    SerialNumber = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    PartNumber = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    HardwareRevision = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    FirmwareVersion = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    Status = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Duts", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "ManufacturingRuns",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    DutId = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    SerialNumber = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    StationId = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    SequenceName = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    SequenceVersion = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    SoftwareVersion = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    StartedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    CompletedAt = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    DurationSeconds = table.Column<double>(type: "double precision", nullable: false),
                    Verdict = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    FirstPass = table.Column<bool>(type: "boolean", nullable: false),
                    FailureCode = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    FailureSummary = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ManufacturingRuns", x => x.Id);
                    table.ForeignKey(
                        name: "FK_ManufacturingRuns_Duts_DutId",
                        column: x => x.DutId,
                        principalTable: "Duts",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "MeasurementRecords",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    ManufacturingRunId = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    DutId = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    StepName = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    MeasurementName = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    Value = table.Column<double>(type: "double precision", nullable: false),
                    Unit = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    LowerLimit = table.Column<double>(type: "double precision", nullable: true),
                    UpperLimit = table.Column<double>(type: "double precision", nullable: true),
                    ExpectedValue = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: true),
                    Verdict = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    FailureCode = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    InstrumentSource = table.Column<string>(type: "character varying(128)", maxLength: 128, nullable: false),
                    Timestamp = table.Column<DateTime>(type: "timestamp with time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MeasurementRecords", x => x.Id);
                    table.ForeignKey(
                        name: "FK_MeasurementRecords_ManufacturingRuns_ManufacturingRunId",
                        column: x => x.ManufacturingRunId,
                        principalTable: "ManufacturingRuns",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Duts_SerialNumber",
                table: "Duts",
                column: "SerialNumber",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_ManufacturingRuns_DutId",
                table: "ManufacturingRuns",
                column: "DutId");

            migrationBuilder.CreateIndex(
                name: "IX_ManufacturingRuns_SerialNumber",
                table: "ManufacturingRuns",
                column: "SerialNumber");

            migrationBuilder.CreateIndex(
                name: "IX_ManufacturingRuns_StartedAt",
                table: "ManufacturingRuns",
                column: "StartedAt");

            migrationBuilder.CreateIndex(
                name: "IX_ManufacturingRuns_Verdict",
                table: "ManufacturingRuns",
                column: "Verdict");

            migrationBuilder.CreateIndex(
                name: "IX_MeasurementRecords_DutId",
                table: "MeasurementRecords",
                column: "DutId");

            migrationBuilder.CreateIndex(
                name: "IX_MeasurementRecords_ManufacturingRunId",
                table: "MeasurementRecords",
                column: "ManufacturingRunId");

            migrationBuilder.CreateIndex(
                name: "IX_MeasurementRecords_Timestamp",
                table: "MeasurementRecords",
                column: "Timestamp");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "MeasurementRecords");

            migrationBuilder.DropTable(
                name: "ManufacturingRuns");

            migrationBuilder.DropTable(
                name: "Duts");
        }
    }
}
