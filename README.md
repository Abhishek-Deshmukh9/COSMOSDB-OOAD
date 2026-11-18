# COSMOSDB-OOAD — Exoplanet Catalog & Comparative Planetology

This workspace contains the **COSMOSDB-OOAD** project, an enterprise-grade object-oriented redesign and implementation of an exoplanet exploration and comparative planetology platform.

---

## 🚀 Active Project Directory

The complete implementation, automated test suite, frontend application, and full documentation are located in:

👉 **[`COSMODB-OOAD/OOAD-Implementation/`](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation)**

Please refer to the primary project documentation:
- **[Main Project README](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/README.md)**: Comprehensive guide, API specification, troubleshooting, and architectural breakdown.
- **[Architecture Specification](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/architecture.md)**: Clean Architecture & SOLID implementation.
- **[Design Decisions & Justifications](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/design-decisions.md)**: Domain-Driven Design & GoF design patterns.
- **[Implementation Completion Report](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/IMPLEMENTATION-COMPLETION-REPORT.md)**: Complete audit and verification report.
- **[UML Diagrams](file:///c:/Users/abhis/Desktop/Pjts/OOAD/COSMODB-OOAD/OOAD-Implementation/docs/OOAD/diagrams)**: All 9 PlantUML (`.puml`) sources and pre-rendered vector graphics (`.svg`).

---

## ⚡ Quick Run Instructions

Run these commands in **two separate PowerShell terminals**:

### Terminal 1: Backend API (FastAPI)
```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\backend
.\.venv\Scripts\python.exe -m uvicorn cosmosdb.api.app:app --host 127.0.0.1 --port 8000 --reload
```
Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Terminal 2: Frontend App (React 18 + Vite)
```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\frontend
npm run dev
```
Web App: [http://localhost:5173](http://localhost:5173)

### Verification Tests
```powershell
cd c:\Users\abhis\Desktop\Pjts\OOAD\COSMODB-OOAD\OOAD-Implementation\backend
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
*(All 28 tests passing).*
