# Deployment and Setup Guide
**Project:** AI-Powered Fault Prediction in 5G Testbed  
**Team:** Team Dynamites

---

## 1. Quick Local Execution (Python + Node.js)

### Prerequisites:
- Python 3.11+
- Node.js 18+ & npm

### Terminal 1: Backend (FastAPI)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run initial model training & validation (generates artifacts/models)
python scripts/train_and_eval.py

# 3. Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **FastAPI Root:** `http://localhost:8000`
- **Swagger Documentation:** `http://localhost:8000/docs`
- **Prometheus Metrics:** `http://localhost:8000/metrics`

### Terminal 2: Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
- **React NOC Dashboard:** `http://localhost:5173`

---

## 2. Docker & Docker Compose Deployment

To launch the full stack including FastAPI, React, Prometheus, and Grafana in isolated containers:

```bash
# Start all services in the background
docker-compose up --build -d

# Check running status
docker-compose ps

# Stop all services
docker-compose down
```

### Exposed Service URLs:
- **React Frontend:** `http://localhost:5173`
- **FastAPI Backend:** `http://localhost:8000`
- **Prometheus UI:** `http://localhost:9090`
- **Grafana Dashboard:** `http://localhost:3001` (Credentials: `admin` / `admin`)

---

## 3. Render Deployment (Backend Only)

The repository includes a [`render.yaml`](../render.yaml) Blueprint, so the first deployment can be created without configuring commands manually.

1. Push the repository to GitHub and open [Render](https://render.com).
2. Select **New > Blueprint** and connect this repository.
3. Keep the detected `render.yaml` service configuration and create the service.
4. When Render asks for `CORS_ORIGINS`, leave it empty for the first health-check deployment or enter your expected frontend origin later. Use comma-separated origins, for example:
   `https://your-app.vercel.app,http://localhost:5173`
5. Wait for the build and deployment to finish. The build installs Python dependencies and trains the included models; the service starts with Render's `$PORT`.
6. Verify these URLs, replacing the host with the URL shown by Render:
   - `https://your-service.onrender.com/health`
   - `https://your-service.onrender.com/docs`

The default database is SQLite. Render's local filesystem is ephemeral, so generated telemetry and alert history can be reset after a restart or redeploy. This is acceptable for the initial demo deployment; use a managed PostgreSQL database for persistent production data.

### Manual Render settings

If you create a Web Service instead of a Blueprint, use:

- **Root Directory:** repository root
- **Runtime:** Python
- **Build Command:** `pip install -r requirements.txt && python scripts/train_and_eval.py`
- **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`
- **Environment Variables:** `ENVIRONMENT=production`, and `CORS_ORIGINS` as a comma-separated list

Do not commit the Render service URL or any database credentials to the repository.

---

## 4. Vercel Deployment (Frontend Later)

After the Render backend is healthy:

1. In Render, set `CORS_ORIGINS` to the final Vercel URL (you may keep `http://localhost:5173` as an additional comma-separated origin), then redeploy.
2. Import this repository into [Vercel](https://vercel.com).
3. Select `frontend` as the **Root Directory**.
4. Use the `Vite` framework preset and keep the default build command (`npm run build`).
5. Add the Vercel environment variable `VITE_API_URL` with the Render URL, for example `https://your-service.onrender.com`, without a trailing slash.
6. Deploy the frontend and test its dashboard, API health check, and simulator controls.
