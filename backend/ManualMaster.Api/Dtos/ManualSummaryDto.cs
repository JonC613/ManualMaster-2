namespace ManualMaster.Api.Dtos;

public record ManualSummaryDto(
    int Id,
    string Title,
    string Category,
    IReadOnlyCollection<string> Tags,
    DateTime UploadDate,
    int Size
);
