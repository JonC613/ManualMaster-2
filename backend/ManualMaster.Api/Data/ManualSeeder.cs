using ManualMaster.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace ManualMaster.Api.Data;

public class ManualSeeder
{
    private readonly ManualContext _context;

    public ManualSeeder(ManualContext context)
    {
        _context = context;
    }

    public async Task SeedAsync(CancellationToken cancellationToken = default)
    {
        if (await _context.Manuals.AnyAsync(cancellationToken))
        {
            return;
        }

        var demoManual = new Manual
        {
            Title = "Getting Started Washer Manual",
            Category = "Appliance",
            Tags = new List<string> { "washer", "laundry", "quick-start" },
            Content = "Welcome to ManualMaster! This sample manual shows how text content can be stored without an uploaded PDF.\n\nSteps:\n1. Install the appliance.\n2. Connect hoses.\n3. Run initial rinse cycle.",
            FileType = null,
            FileName = null,
            FileData = null,
            Size = 0,
            SourceUrl = null,
            SearchQuery = null,
            UploadDate = DateTime.UtcNow
        };

        _context.Manuals.Add(demoManual);
        await _context.SaveChangesAsync(cancellationToken);
    }
}
