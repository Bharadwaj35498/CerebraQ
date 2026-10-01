# CerebraQ frontend implementation

This is a research prototype, not a clinical system. The existing `frontend/README.md`, backend, model artifacts, datasets, and scientific results have not been modified.

## Run locally

From `frontend/`, run `npm install`, `npm run dev`, `npm run build`, and `npx tsc --noEmit`. Start the Flask backend separately with the repository's Python requirements and `python backend/app.py` from the repository root. The development server proxies `/api` to `http://127.0.0.1:5000`. Open the URL reported by Vite. Ensure your package manager supports the versions declared in `package.json`. A lockfile has not been generated because this editing environment has no npm execution capability.

## Configuration

Copy `.env.example` to `.env.local` if overrides are needed. Leave `VITE_API_BASE_URL` empty for the development proxy. For deployment, configure a same-origin `/api` reverse proxy or enable CORS on the Flask server in a separate, reviewed backend change; direct cross-origin `VITE_API_BASE_URL=http://127.0.0.1:5000` requests are blocked unless CORS is enabled. `127.0.0.1` is the **browser's machine**, not the deployment server. Set `VITE_USE_MOCK=false` for actual Flask data. If set to `true`, the UI shows `DEMO DATA`, but the mock adapter intentionally returns an unavailable state rather than manufacturing research values.

## Existing API

The frontend uses `GET /api/health`, `/api/patients`, `/api/metrics`, `/api/patient/<id>`, and `/api/explanation/<id>`. React Query caches responses in memory only. Only the active case and optional job identifiers are stored in `sessionStorage`. Locally selected files are previewed but never submitted or stored persistently.

## Current capability limits

The current Flask server has no upload or analysis job route; the Analyze button is disabled. There is no real progress or job status to display. The explanation endpoint returns image availability and filename but does not serve the PNG. The patient report's `visualization` is an absolute path on another machine, not a safe browser URL; it must not be used in an `<img>`. Image overlays, original MRI slices, modality switching, NIfTI volume rendering, opacity and slice sliders require a reviewed server image/slice contract and cannot honestly be enabled yet. Confusion-matrix counts, uncertainty estimates, quantum circuit depth and measured stage durations are also absent from the API. The quantum diagram is schematic, not an execution trace.

## Validation required before merge

This environment has GitHub file editing but no terminal or installed npm dependencies. **Build, TypeScript type-check, browser tests, responsive checks, and API integration tests have not been run.** From `frontend/`, run `npm install && npm run build && npx tsc --noEmit`. Manually verify keyboard navigation, dark/light contrast, viewport widths 375/768/1280, print layout, loading/error/empty states, and live Flask requests before deployment. Do not merge solely on the basis of code review.
