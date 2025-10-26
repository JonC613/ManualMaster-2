using System.Text;
using ManualMaster.Api.Data;
using ManualMaster.Api.Dtos;
using ManualMaster.Api.Extensions;
using ManualMaster.Api.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace ManualMaster.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ManualsController : ControllerBase
{
    private readonly ManualContext _context;

    public ManualsController(ManualContext context)
    {
        _context = context;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<ManualSummaryDto>>> GetManuals(
        [FromQuery] string? category,
        [FromQuery] string? search)
    {
        IQueryable<Manual> query = _context.Manuals.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(category))
        {
            var normalizedCategory = category.Trim();
            query = query.Where(m => EF.Functions.Like(m.Category, normalizedCategory));
        }

        var manuals = await query.ToListAsync();

        if (!string.IsNullOrWhiteSpace(search))
        {
            var normalizedSearch = search.Trim();
            manuals = manuals
                .Where(m =>
                    m.Title.Contains(normalizedSearch, StringComparison.OrdinalIgnoreCase) ||
                    m.Category.Contains(normalizedSearch, StringComparison.OrdinalIgnoreCase) ||
                    m.Tags.Any(tag => tag.Contains(normalizedSearch, StringComparison.OrdinalIgnoreCase)) ||
                    m.Content.Contains(normalizedSearch, StringComparison.OrdinalIgnoreCase))
                .ToList();
        }

        var results = manuals
            .OrderByDescending(m => m.UploadDate)
            .Select(m => m.ToSummaryDto())
            .ToList();

        return Ok(results);
    }

    [HttpGet("categories")]
    public async Task<ActionResult<IEnumerable<string>>> GetCategories()
    {
        var dbCategories = await _context.Manuals
            .Select(m => m.Category)
            .Distinct()
            .ToListAsync();

        var categories = ManualDefaults.Categories
            .Union(dbCategories, StringComparer.OrdinalIgnoreCase)
            .OrderBy(c => c)
            .ToList();

        return Ok(categories);
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<ManualDto>> GetManual(int id)
    {
        var manual = await _context.Manuals.AsNoTracking().FirstOrDefaultAsync(m => m.Id == id);

        if (manual is null)
        {
            return NotFound();
        }

        return Ok(manual.ToDto());
    }

    [HttpGet("{id:int}/download")]
    public async Task<IActionResult> DownloadManual(int id)
    {
        var manual = await _context.Manuals.AsNoTracking().FirstOrDefaultAsync(m => m.Id == id);

        if (manual is null || manual.FileData is null)
        {
            return NotFound();
        }

        var fileName = string.IsNullOrWhiteSpace(manual.FileName) ? $"manual-{id}.bin" : manual.FileName;
        var fileType = string.IsNullOrWhiteSpace(manual.FileType) ? "application/octet-stream" : manual.FileType;

        return File(manual.FileData, fileType, fileName);
    }

    [HttpPost]
    public async Task<ActionResult<ManualDto>> CreateManual([FromBody] ManualCreateRequest request)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        var manual = new Manual
        {
            Title = request.Title.Trim(),
            Category = request.Category.Trim(),
            Tags = request.Tags
                .Select(tag => tag.Trim())
                .Where(tag => !string.IsNullOrWhiteSpace(tag))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList(),
            Content = request.Content,
            FileName = request.FileName,
            FileType = request.FileType,
            SourceUrl = request.SourceUrl,
            SearchQuery = request.SearchQuery,
            UploadDate = DateTime.UtcNow
        };

        if (!string.IsNullOrWhiteSpace(request.FileDataBase64))
        {
            try
            {
                manual.FileData = Convert.FromBase64String(request.FileDataBase64);
                manual.Size = manual.FileData.Length;
            }
            catch (FormatException)
            {
                return BadRequest("Uploaded file could not be decoded from base64.");
            }
        }
        else
        {
            manual.Size = Encoding.UTF8.GetByteCount(manual.Content);
        }

        _context.Manuals.Add(manual);
        await _context.SaveChangesAsync();

        return CreatedAtAction(nameof(GetManual), new { id = manual.Id }, manual.ToDto());
    }

    [HttpPut("{id:int}")]
    public async Task<ActionResult<ManualDto>> UpdateManual(int id, [FromBody] ManualUpdateRequest request)
    {
        if (!ModelState.IsValid)
        {
            return ValidationProblem(ModelState);
        }

        var manual = await _context.Manuals.FirstOrDefaultAsync(m => m.Id == id);
        if (manual is null)
        {
            return NotFound();
        }

        manual.Title = request.Title.Trim();
        manual.Category = request.Category.Trim();
        manual.Tags = request.Tags
            .Select(tag => tag.Trim())
            .Where(tag => !string.IsNullOrWhiteSpace(tag))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
        manual.Content = request.Content;
        manual.FileName = request.FileName;
        manual.FileType = request.FileType;
        manual.SourceUrl = request.SourceUrl;
        manual.SearchQuery = request.SearchQuery;
        manual.UploadDate = DateTime.UtcNow;

        if (!string.IsNullOrWhiteSpace(request.FileDataBase64))
        {
            try
            {
                manual.FileData = Convert.FromBase64String(request.FileDataBase64);
                manual.Size = manual.FileData.Length;
            }
            catch (FormatException)
            {
                return BadRequest("Uploaded file could not be decoded from base64.");
            }
        }
        else
        {
            manual.FileData = null;
            manual.Size = Encoding.UTF8.GetByteCount(manual.Content);
        }

        await _context.SaveChangesAsync();

        return Ok(manual.ToDto());
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> DeleteManual(int id)
    {
        var manual = await _context.Manuals.FirstOrDefaultAsync(m => m.Id == id);
        if (manual is null)
        {
            return NotFound();
        }

        _context.Manuals.Remove(manual);
        await _context.SaveChangesAsync();

        return NoContent();
    }
}
