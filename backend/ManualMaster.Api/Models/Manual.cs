using System.ComponentModel.DataAnnotations;

namespace ManualMaster.Api.Models;

public class Manual
{
    public int Id { get; set; }

    [Required]
    [MaxLength(255)]
    public string Title { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    public string Category { get; set; } = "Other";

    public List<string> Tags { get; set; } = new();

    [Required]
    public string Content { get; set; } = string.Empty;

    public byte[]? FileData { get; set; }

    [MaxLength(50)]
    public string? FileType { get; set; }

    [MaxLength(255)]
    public string? FileName { get; set; }

    public DateTime UploadDate { get; set; } = DateTime.UtcNow;

    public int Size { get; set; }

    [MaxLength(500)]
    public string? SourceUrl { get; set; }

    [MaxLength(255)]
    public string? SearchQuery { get; set; }
}
