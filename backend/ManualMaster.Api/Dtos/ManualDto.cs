namespace ManualMaster.Api.Dtos;

public record ManualDto(
    int Id,
    string Title,
    string Category,
    IReadOnlyCollection<string> Tags,
    string Content,
    string? FileName,
    string? FileType,
    int Size,
    DateTime UploadDate,
    string? SourceUrl,
    string? SearchQuery,
    string? FileDataBase64
);
