# ManualMaster .NET 8 API

This folder contains the ASP.NET Core Web API that powers the ManualMaster application. The service exposes endpoints for managing manuals, uploading optional binary attachments and browsing categories.

## Getting started

1. Install the .NET 8 SDK.
2. From the `backend/ManualMaster.Api` directory restore packages and run the API:

```bash
dotnet restore
dotnet run
```

The API listens on `https://localhost:5001` / `http://localhost:5000` by default. Update the `ConnectionStrings:Manuals` entry in `appsettings.json` to point at a different SQLite database if needed.

## Available endpoints

- `GET /api/manuals` – list manuals with optional `category` and `search` query parameters.
- `GET /api/manuals/{id}` – fetch a single manual including content and attachment metadata.
- `GET /api/manuals/{id}/download` – download the stored binary file if available.
- `POST /api/manuals` – create a manual. Accepts JSON with fields matching `ManualCreateRequest` (including optional `fileDataBase64`).
- `PUT /api/manuals/{id}` – update an existing manual.
- `DELETE /api/manuals/{id}` – remove a manual.
- `GET /api/manuals/categories` – list categories merged from defaults and existing entries.

Swagger UI is enabled in development builds for quick exploration of the contract.
