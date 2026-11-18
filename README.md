# COSMOSDB-OOAD — Exoplanet Catalog & Comparative Planetology

Welcome to the **COSMOSDB-OOAD** repository.

This project represents the complete, production-grade object-oriented redesign and implementation of the **COSMOSDB** exoplanet catalog and comparative planetology platform, built for the **Object-Oriented Analysis and Design (OOAD)** curriculum.

> 🚀 **The active, modern Clean Architecture implementation lives in [`OOAD-Implementation/`](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation).**  
> For the comprehensive technical specification, architecture diagrams, and API docs, please refer directly to:  
> **[OOAD-Implementation/README.md](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/README.md)**

---

## ⚡ Quick Start: Running the Application

To run the complete application, execute the following commands in **two separate PowerShell terminals**:

### 1. Backend API (FastAPI)

```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\backend
.\.venv\Scripts\python.exe -m uvicorn cosmosdb.api.app:app --host 127.0.0.1 --port 8000 --reload
```
- Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend Application (React + Vite)

```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

*(Make sure your local MySQL service `MySQL80` is running. The verified backend database credentials are `cosmos` / `cosmos123` on `cosmosdb`).*

---

## 🏗️ Repository Layout

- **[`OOAD-Implementation/`](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation):** **Primary Active Implementation**
  - **`backend/`:** FastAPI service built strictly with Clean Architecture & Domain-Driven Design (Domain $\to$ Application $\to$ Infrastructure $\to$ Presentation).
  - **`frontend/`:** Modern React 18 + TypeScript + Vite SPA with 3D orbit simulation (`Three.js`), radial ESI gauges, and 9-chart ECharts mission control analytics dashboard.
  - **`database/`:** Normalized MySQL schema DDL (`schema.sql`).
  - **`docs/OOAD/`:** Complete OOAD documentation:
    - [architecture.md](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/architecture.md): Clean Architecture specification and DIP mapping.
    - [design-decisions.md](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/design-decisions.md): Architectural decisions and justifications.
    - [IMPLEMENTATION-COMPLETION-REPORT.md](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/IMPLEMENTATION-COMPLETION-REPORT.md): Audit and verification report.
    - [diagrams/](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams): All 9 PlantUML sources (`.puml`) and rendered vector diagrams (`.svg`).
- **Legacy Files (Root level):** Archived baseline prototype assets retained for historical evaluation and assignment requirement traceability.

---

## 🧪 Verification & Test Suite

Run the full automated test suite (28/28 tests passing):

```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\backend
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Please see the [Full Documentation & Specification in OOAD-Implementation/README.md](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/README.md) for full architectural breakdown and API documentation.
