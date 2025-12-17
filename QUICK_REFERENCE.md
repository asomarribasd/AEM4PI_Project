# Quick Reference - Lost Pet Intelligence System

## 🚀 Quick Start

### 1. Setup (One Time)
```bash
# Install dependencies
pip install openai pydantic pillow python-dotenv fastapi uvicorn requests

# Configure environment
# Edit .env file with your OPENAI_API_KEY
```

### 2. Run the System

**Option A: Command Line**
```bash
python src/main.py
```

**Option B: REST API**
```bash
# Terminal 1
python run_api.py

# Terminal 2
python test_api.py
```

**Option C: Interactive API Docs**
```bash
python run_api.py
# Open: http://localhost:8000/docs
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | Main orchestration pipeline |
| `src/api/main.py` | REST API server |
| `run_api.py` | Start API server |
| `test_api.py` | Test API endpoints |
| `run_tests.py` | Run all test cases |
| `.env` | Configuration (API keys) |

---

## 🔌 API Endpoints

```bash
# Health check
GET http://localhost:8000/health

# Report lost pet
POST http://localhost:8000/api/v1/report/lost
  - province: "San José"
  - canton: "Escazú"
  - district: "San Antonio"
  - description: "White and brown dog..."

# Report sighting
POST http://localhost:8000/api/v1/report/sighting
  (same parameters)

# Search
GET http://localhost:8000/api/v1/search?province=San+José&species=dog
```

---

## 📊 Test Results

```
✓ valid_case_1: Dog - HIGH confidence
✓ valid_case_2: Cat - HIGH confidence
✓ edge_case_1: Minimal - NO matches
✓ invalid_case_1: Bad location - Rejected
✓ invalid_case_2: Bad province - Rejected

Result: 5/5 PASSED
```

---

## ⚙️ Configuration

**Environment Variables (.env):**
```
OPENAI_API_KEY=sk-...
USE_EMBEDDINGS=false  # Set to true for real mode
DEBUG=False
```

---

## 📖 Documentation

- `IMPLEMENTATION_PLAN.md` - Complete implementation guide
- `QUICK_START.md` - Getting started guide
- `API_DOCUMENTATION.md` - REST API reference
- `PHASE5_10_SUMMARY.md` - Latest changes summary

---

## 🐛 Troubleshooting

**API won't start:**
- Check port 8000 is free
- Verify .env exists with API key

**Tests failing:**
- Ensure venv is activated
- Check all dependencies installed

**No matches found:**
- Normal for edge cases
- Check mock database has data

---

## 📞 Need Help?

1. Check `/docs` endpoint: http://localhost:8000/docs
2. Review QUICK_START.md
3. Check API_DOCUMENTATION.md for examples

---

**System Status: ✅ Fully Operational**
