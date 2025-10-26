using ManualMaster.Api.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("Manuals")
    ?? builder.Configuration["MANUALS_CONNECTION"]
    ?? "Data Source=manuals.db";

builder.Services.AddDbContext<ManualContext>(options =>
    options.UseSqlite(connectionString));

builder.Services.AddScoped<ManualSeeder>();

builder.Services.AddControllers();

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options =>
{
    options.AddPolicy("default", policy =>
    {
        policy
            .AllowAnyHeader()
            .AllowAnyMethod()
            .AllowCredentials()
            .SetIsOriginAllowed(_ => true);
    });
});

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ManualContext>();
    await context.Database.EnsureCreatedAsync();

    var seeder = scope.ServiceProvider.GetRequiredService<ManualSeeder>();
    await seeder.SeedAsync();
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("default");
app.UseAuthorization();
app.MapControllers();

app.Run();
