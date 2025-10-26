using ManualMaster.Api.Dtos;
using ManualMaster.Api.Models;

namespace ManualMaster.Api.Extensions;

public static class ManualMappingExtensions
{
    public static ManualSummaryDto ToSummaryDto(this Manual manual) =>
        new(
            manual.Id,
            manual.Title,
            manual.Category,
            manual.Tags.AsReadOnly(),
            manual.UploadDate,
            manual.Size
        );

    public static ManualDto ToDto(this Manual manual) =>
        new(
            manual.Id,
            manual.Title,
            manual.Category,
            manual.Tags.AsReadOnly(),
            manual.Content,
            manual.FileName,
            manual.FileType,
            manual.Size,
            manual.UploadDate,
            manual.SourceUrl,
            manual.SearchQuery,
            manual.FileData is null ? null : Convert.ToBase64String(manual.FileData)
        );
}
