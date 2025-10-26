# ManualMaster React front end

This directory hosts the Vite + React client for the ManualMaster application. It communicates with the .NET 8 API located under `../backend/ManualMaster.Api`.

## Setup

1. Install Node.js 18 or newer.
2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

By default the app expects the API to be reachable at `http://localhost:5000/api`. Override this by creating a `.env` file with `VITE_API_BASE_URL`.

## Production build

To create an optimized build run:

```bash
npm run build
```

The output will be written to the `dist` folder.
