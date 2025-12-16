# Quick Start Guide - AI Multi-Agent Lost Pet System

## 🚀 Setup & Running the System

### Step 1: Install Dependencies

```powershell
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure Environment

```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

**Minimum required in `.env`:**
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_VISION_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
USE_EMBEDDINGS=false  # Set to false for testing without API costs
```

### Step 3: Run the System

```powershell
# Run with example data (no images, no API costs)
python src/main.py
```

---

## 🧪 Testing Options

### Option 1: Mock Mode (No API Costs)
Perfect for development and testing logic without spending on API calls.

```
USE_EMBEDDINGS=false
```
- Uses mock similarity algorithm
- No OpenAI embedding calls
- Fast and free
- Good for testing flow

### Option 2: Real Embeddings (API Costs)
Uses actual vector embeddings for better matching accuracy.

```
USE_EMBEDDINGS=true
```
- Real vector similarity search
- Better matching accuracy
- Costs: ~$0.0001 per embedding
- Requires OpenAI API key

### Option 3: With Images (Full Pipeline)
Full multimodal processing with vision AI.

```python
# Modify example in src/main.py
example_input = UserInput(
    images=["path/to/image1.jpg", "path/to/image2.jpg"],
    description="...",
    location=Location(...),
    report_type="lost"
)
```
- Full vision AI analysis
- Costs: ~$0.01-0.05 per image
- Most accurate results

---

## 📂 Project Structure

```
AEM4PI_Project/
├── src/
│   ├── agents/
│   │   ├── visual_extractor_agent.py   # Agent 1: Image & Text Analysis
│   │   ├── similarity_agent.py         # Agent 2: Matching & Search
│   │   └── decision_agent.py           # Agent 3: Explanations
│   ├── models/
│   │   ├── pet_models.py               # Pet data models
│   │   └── match_models.py             # Match result models
│   ├── utils/
│   │   ├── data_access.py              # Mock database
│   │   ├── image_utils.py              # Image processing
│   │   └── embedding_utils.py          # Vector operations
│   └── main.py                         # Main orchestration
├── data/
│   └── mock_database.json              # Test data (8 lost pets, 5 sightings)
├── examples/                           # 5 test cases
├── tests/
│   └── test_phase1_2.py               # Validation tests
├── requirements.txt
├── .env.example
└── IMPLEMENTATION_PLAN.md
```

---

## 🔧 Common Issues & Solutions

### Issue: "OPENAI_API_KEY not found"
**Solution:** Create `.env` file from `.env.example` and add your API key

### Issue: "Module not found"
**Solution:** Make sure you're in the project root and have activated venv
```powershell
cd c:\Proyectos\AEM4PI_Project
.\venv\Scripts\Activate.ps1
```

### Issue: "Image validation failed"
**Solution:** Start with mock mode (no images) or use supported formats (JPEG, PNG)

### Issue: High API costs
**Solution:** Set `USE_EMBEDDINGS=false` and remove image paths from test input

---

## 📊 Expected Output

When you run the system, you'll see:

```
============================================================
INITIALIZING AI MULTI-AGENT SYSTEM
============================================================

[Setup] Initializing Agent 1: Visual & Text Extractor...
  ✓ Agent 1 ready

[Setup] Initializing Agent 2: Match & Similarity...
  ✓ Agent 2 ready (embeddings: false)

[Setup] Initializing Agent 3: Decision & Explanation...
  ✓ Agent 3 ready

============================================================
ALL AGENTS INITIALIZED SUCCESSFULLY
============================================================

============================================================
PROCESSING PET REPORT
============================================================
Report Type: lost
Location: Escazú, San José
Images: 0
============================================================

[Agent 1: Visual & Text Extractor] Starting extraction...
  - Analyzing 0 images...
  - Image analysis complete: None, None
  - Analyzing text description...
  - Text analysis complete
  - Merging and validating data...
[Agent 1] ✓ Extraction complete!
  Result: dog | medium | Colors: ['white', 'brown']
  Features: ['black spot on left ear', 'red collar with bell']

[Agent 2: Match & Similarity] Starting search...
  - Searching with mock similarity...
  - Found 8 potential matches
  - 3 matches above threshold (0.6)
[Agent 2] ✓ Search complete!
  Confidence: high
  Top match: LOST-001 (score: 0.900)

[Agent 3: Decision & Explanation] Generating output...
  - Generating explanation...
  - Generating recommendations...
[Agent 3] ✓ Output generation complete!
  Confidence: High confidence match found!
  Recommendations: 6

============================================================
PROCESSING COMPLETE
============================================================
Total Processing Time: 3.45 seconds
============================================================

============================================================
RESULTS
============================================================

📋 ENRICHED PET PROFILE:
  Species: dog
  Size: medium
  Colors: white, brown
  Features: black spot on left ear, red collar with bell
  Breed: Mixed breed

🔍 MATCH RESULTS:
  High confidence match found! This could be your pet.
  Total candidates found: 8
  Matches above threshold: 3

  🎯 TOP MATCH:
     ID: LOST-001
     Type: lost
     Similarity: 90.0%
     Distance: 1.2km
     Days ago: 6
     Reasons: Same species, Same colors, Similar features

💬 EXPLANATION:
  Found a strong match in your area! Report LOST-001 has very similar 
  characteristics including white and brown coloring and a black spot 
  marking. The location is only 1.2km away from where your pet was last seen.

✅ RECOMMENDED ACTIONS:
  1. Contact the reporter of LOST-001 immediately - this is a strong match
  2. Bring photos of your pet when meeting to verify identity
  3. Ask specific questions about distinctive features to confirm
  4. Be prepared to provide proof of ownership if the pet is found
  5. Visit the sighting location (Escazú) as soon as possible
  6. When posting, emphasize distinctive features: black spot on left ear

⏱️  Processing time: 3.45 seconds

============================================================

✓ Results saved to: output/results_20251216_143022.json
```

---

## 🎯 What's Working

- ✅ All 3 agents fully functional
- ✅ Sequential pipeline working
- ✅ Mock database with 13 test records
- ✅ Pydantic validation throughout
- ✅ Error handling and fallbacks
- ✅ Natural language explanations
- ✅ Actionable recommendations
- ✅ JSON export of results
- ✅ Performance tracking

---

## ⏭️ Next Development Steps

1. **Test with examples** - Run through all 5 test cases
2. **Add documentation** - Complete proposal.md and README
3. **Build API** - FastAPI endpoints for web integration
4. **Deploy** - Make it accessible via web interface

---

## 📝 Notes

- The system works WITHOUT images by analyzing text descriptions
- Mock mode is perfect for development (no API costs)
- Real embeddings improve accuracy but cost ~$0.0001 per search
- Vision AI improves extraction but costs ~$0.01-0.05 per image
- All results are saved to `output/` directory as JSON

---

## 🆘 Need Help?

Check these files:
- `IMPLEMENTATION_PLAN.md` - Full project plan
- `PHASE3_4_SUMMARY.md` - Detailed implementation summary
- `examples/` - Test case examples
- `.env.example` - Configuration template

---

**You're all set! 🎉**

The core multi-agent system is ready to process lost pet reports!
