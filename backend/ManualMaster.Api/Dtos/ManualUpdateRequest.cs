using System.ComponentModel.DataAnnotations;

namespace ManualMaster.Api.Dtos;

public class ManualUpdateRequest
{
    [Required]
    [MaxLength(255)]
    public string Title { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    public string Category { get; set; } = "Other";

    public List<string> Tags { get; set; } = new();

    [Required]
    public string Content { get; set; } = string.Empty;

    public string? FileName { get; set; }

    public string? FileType { get; set; }

    public string? FileDataBase64 { get; set; }

    public string? SourceUrl { get; set; }

    public string? SearchQuery { get; set; }
}
