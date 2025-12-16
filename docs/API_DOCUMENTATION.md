# Lost Pet Intelligence API Documentation

## Overview

The Lost Pet Intelligence API provides AI-powered matching between lost pets and sightings using a multi-agent system.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required (development mode).

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running and agents are initialized.

**Response:**
```json
{
  "status": "healthy",
  "agents_initialized": true,
  "config_loaded": true
}
```

---

### 2. Report Lost Pet

**POST** `/api/v1/report/lost`

Submit a lost pet report with optional images.

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| province | string | Yes | One of: San José, Alajuela, Cartago, Heredia, Guanacaste, Puntarenas, Limón |
| canton | string | Yes | Canton name |
| district | string | Yes | District name |
| description | string | Yes | Detailed pet description (min 10 characters) |
| additional_details | string | No | Additional location info |
| images | file[] | No | Pet images (max 5, 5MB each, JPEG/PNG/GIF/BMP/WebP) |

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/report/lost" \
  -F "province=San José" \
  -F "canton=Escazú" \
  -F "district=San Antonio" \
  -F "description=Medium-sized white and brown dog with black spot on left ear" \
  -F "additional_details=Near the park"
```

**Example Request (Python):**
```python
import requests

data = {
    "province": "San José",
    "canton": "Escazú",
    "district": "San Antonio",
    "description": "Medium-sized white and brown dog with black spot on left ear"
}

response = requests.post(
    "http://localhost:8000/api/v1/report/lost",
    data=data
)

print(response.json())
```

**Response:**
```json
{
  "success": true,
  "result": {
    "enriched_profile": {
      "species": "dog",
      "size": "medium",
      "colors": ["white", "brown"],
      "features": ["black spot on left ear"]
    },
    "matches": {
      "confidence_level": "high",
      "candidates": [...],
      "top_match": {
        "match_id": "LOST-001",
        "similarity_score": 0.88,
        "location_distance_km": 3.0
      }
    },
    "explanation": "There are two promising leads...",
    "recommended_actions": [
      "Contact the reporter of LOST-001 immediately",
      "Bring photos of your pet when meeting"
    ]
  }
}
```

---

### 3. Report Sighting

**POST** `/api/v1/report/sighting`

Submit a pet sighting report with optional images.

**Content-Type:** `multipart/form-data`

**Parameters:** Same as `/api/v1/report/lost`

**Example Request (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append('province', 'San José');
formData.append('canton', 'Moravia');
formData.append('district', 'San Vicente');
formData.append('description', 'Gray and white cat with green eyes');

fetch('http://localhost:8000/api/v1/report/sighting', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

### 4. Search

**GET** `/api/v1/search`

Search for pets in the database (basic filtering).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| province | string | No | Filter by province |
| species | string | No | Filter by species (dog/cat) |
| size | string | No | Filter by size (small/medium/large) |
| limit | integer | No | Max results (default: 10) |

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/search?province=San%20José&species=dog&limit=5"
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Maximum 5 images allowed"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "province"],
      "msg": "Province must be one of: San José, Alajuela..."
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message here"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Agents not initialized"
}
```

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces allow you to test endpoints directly from your browser.

---

## Testing the API

### Option 1: Using the Test Script

```bash
# Terminal 1: Start the API server
python run_api.py

# Terminal 2: Run the test client
python test_api.py
```

### Option 2: Using cURL

```bash
# Test health check
curl http://localhost:8000/health

# Test lost pet report
curl -X POST "http://localhost:8000/api/v1/report/lost" \
  -F "province=San José" \
  -F "canton=Escazú" \
  -F "district=San Antonio" \
  -F "description=White dog with brown patches, black spot on ear"
```

### Option 3: Using Swagger UI

1. Start the API: `python run_api.py`
2. Open browser: http://localhost:8000/docs
3. Try out any endpoint with the interactive interface

---

## Integration with Webpage

### HTML Form Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Report Lost Pet</title>
</head>
<body>
    <h1>Report Lost Pet</h1>
    <form id="lostPetForm">
        <label>Province:</label>
        <select name="province" required>
            <option>San José</option>
            <option>Alajuela</option>
            <option>Cartago</option>
            <option>Heredia</option>
            <option>Guanacaste</option>
            <option>Puntarenas</option>
            <option>Limón</option>
        </select>
        
        <label>Canton:</label>
        <input type="text" name="canton" required>
        
        <label>District:</label>
        <input type="text" name="district" required>
        
        <label>Description:</label>
        <textarea name="description" required minlength="10"></textarea>
        
        <label>Images (optional, max 5):</label>
        <input type="file" name="images" multiple accept="image/*">
        
        <button type="submit">Submit Report</button>
    </form>

    <script>
        document.getElementById('lostPetForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            
            const response = await fetch('http://localhost:8000/api/v1/report/lost', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            console.log('Result:', result);
            
            // Display results to user
            alert('Report submitted! Check console for results.');
        });
    </script>
</body>
</html>
```

---

## Response Data Structure

### Confidence Levels

- **high**: Strong match found (similarity ≥ 0.8)
- **medium**: Moderate match (0.6 ≤ similarity < 0.8)
- **low**: Weak match (similarity < 0.6)
- **none**: No matches above threshold

### Match Candidate Fields

- `match_id`: Unique identifier for the match
- `report_type`: "lost" or "sighting"
- `similarity_score`: 0.0 to 1.0
- `matching_reasons`: List of why it matches
- `location_distance_km`: Distance in kilometers
- `days_since_report`: Days since report was created

---

## Performance

- Average processing time: **3-6 seconds** per report
- Supports concurrent requests
- Mock mode (USE_EMBEDDINGS=false): No API costs, instant processing
- Real mode (USE_EMBEDDINGS=true): Uses OpenAI API, ~2-3 seconds extra

---

## Troubleshooting

### API won't start
- Check that port 8000 is available
- Ensure `.env` file exists with `OPENAI_API_KEY`
- Verify Python dependencies are installed

### "Agents not initialized" error
- Wait a few seconds after starting the API
- Check `/health` endpoint to verify initialization

### Image upload fails
- Maximum 5 images per request
- Each image must be under 5MB
- Supported formats: JPEG, PNG, GIF, BMP, WebP

---

## Development Notes

### Running in Production

For production deployment, update `src/api/main.py`:

1. Set specific CORS origins (replace `"*"`)
2. Add authentication middleware
3. Use environment-based configuration
4. Set up proper logging
5. Use a production ASGI server (Gunicorn + Uvicorn)

### Adding New Endpoints

Add new routes to `src/api/main.py`:

```python
@app.post("/api/v1/your-endpoint")
async def your_function():
    # Your logic here
    pass
```

---

## Support

For issues or questions:
- Check interactive docs: http://localhost:8000/docs
- Review logs in the terminal where API is running
- Consult `QUICK_START.md` for setup help
