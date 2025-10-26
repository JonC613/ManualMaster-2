using System.Text.Json;
using ManualMaster.Api.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;

namespace ManualMaster.Api.Data;

public class ManualContext : DbContext
{
    public ManualContext(DbContextOptions<ManualContext> options) : base(options)
    {
    }

    public DbSet<Manual> Manuals => Set<Manual>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var tagsConverter = new ValueConverter<List<string>, string>(
            v => JsonSerializer.Serialize(v ?? new List<string>(), (JsonSerializerOptions?)null),
            v => string.IsNullOrWhiteSpace(v)
                ? new List<string>()
                : JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions?)null) ?? new List<string>()
        );

        modelBuilder.Entity<Manual>(entity =>
        {
            entity.Property(e => e.Tags)
                .HasConversion(tagsConverter)
                .HasColumnType("TEXT");

            entity.Property(e => e.UploadDate)
                .HasDefaultValueSql("CURRENT_TIMESTAMP");

            entity.Property(e => e.Content)
                .HasColumnType("TEXT");
        });
    }
}
