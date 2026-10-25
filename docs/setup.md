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

## 3. Render Deployment (Backend)

The backend is 100% cloud-ready for Render Web Services:

1. Connect your GitHub repository to [Render.com](https://render.com).
2. Choose **New Web Service**.
3. Set the following settings:
   - **Environment:** `Python` or `Docker`
   - **Build Command:** `pip install -r requirements.txt && python scripts/train_and_eval.py`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `ENVIRONMENT=production`
   - `DATABASE_URL=sqlite:///./data/5g_telemetry.db` (or attach a Render Managed PostgreSQL database URI)
5. Click **Deploy**. Note your public URL (e.g., `https://fiveg-fault-backend.onrender.com`).

---

## 4. Vercel Deployment (Frontend)

The frontend is optimized for zero-config deployment on Vercel:

1. Import your repository into [Vercel](https://vercel.com).
2. Select the `frontend` folder as the **Root Directory**.
3. Framework Preset: `Vite`.
4. Configure Environment Variable:
   - `VITE_API_URL`: Your deployed Render backend URL (e.g., `https://fiveg-fault-backend.onrender.com`).
5. Click **Deploy**. Vercel will build and serve your React app globally on edge CDNs!
