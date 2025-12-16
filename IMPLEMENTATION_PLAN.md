# AI Multi-Agent Lost Pet Intelligence System - Implementation Plan

## Project Overview
Building a multi-agent AI system for a lost pets platform that uses computer vision, NLP, and vector search to improve pet recovery outcomes.

---

## Phase 1: Project Setup & Environment Configuration ✅ COMPLETED

### 1.1 Repository Structure Creation ✅
- [x] Create `/src` directory with subdirectories:
  - [x] `/src/agents` - Agent implementations
  - [x] `/src/models` - Pydantic data models
  - [x] `/src/utils` - Utility functions
- [x] Create `/docs` directory for documentation
- [x] Create `/examples` directory with test case subdirectories:
  - [x] `valid_case_1/` - Complete, well-formed report
  - [x] `valid_case_2/` - Another valid scenario
  - [x] `edge_case_1/` - Unusual but valid case
  - [x] `invalid_case_1/` - Missing required fields
  - [x] `invalid_case_2/` - Invalid image format or corrupted data
- [x] Create `/data` directory for mock database
- [x] Create `/tests` directory for validation scripts

### 1.2 Configuration Files ✅
- [x] Create `requirements.txt` with pinned versions including:
  - OpenAI SDK (1.54.3)
  - LangChain ecosystem (0.3.x)
  - ChromaDB (0.5.15) for vector store
  - Pydantic v2 (2.9.2)
  - Pillow (10.4.0) for image processing
  - python-dotenv (1.0.1)
  - Langfuse (2.52.1) for tracing
  - pytest for testing
- [x] Create `.env.example` template with:
  - OpenAI API keys placeholders
  - Model configurations (GPT-4o, embeddings)
  - Vector store settings
  - Application parameters
- [x] Update `.gitignore` to exclude:
  - `.env` files
  - `__pycache__/` and `*.pyc`
  - Vector store data
  - Temporary files

### 1.3 Development Environment
- [ ] Set up Python virtual environment (Ready to do)
- [ ] Install all dependencies from requirements.txt
- [ ] Create .env file from .env.example and add OpenAI API key
- [ ] Test API credentials

---

## Phase 2: Data Models & Validation (Pydantic) ✅ COMPLETED

### 2.1 Core Pet Models (`/src/models/pet_models.py`) ✅
- [x] Create `Location` model:
  - province: str (validated against Costa Rica provinces)
  - canton: str (required, validated non-empty)
  - district: str (required, validated non-empty)
  - additional_details: Optional[str]
- [x] Create `SpeciesType` and `SizeType` enums for standardization
- [x] Create `PetDescription` model:
  - species: SpeciesType (dog, cat, other)
  - size: SizeType (small, medium, large)
  - colors: List[str] (min 1, normalized to lowercase)
  - distinctive_features: List[str] (cleaned and validated)
  - breed: Optional[str]
  - approximate_age: Optional[str]
  - last_seen_location: Location
  - last_seen_date: Optional[str]
- [x] Create `UserInput` model:
  - images: List[str] (file paths, max 5)
  - description: str (min 10 characters)
  - location: Location
  - contact_info: Optional[str]
  - report_type: str (validated: 'lost' or 'sighting')
- [x] Create `PetReport` model for database storage

### 2.2 Match Models (`/src/models/match_models.py`) ✅
- [x] Create `ConfidenceLevel` enum (HIGH, MEDIUM, LOW, NONE)
- [x] Create `MatchCandidate` model:
  - match_id: str
  - report_type: str
  - similarity_score: float (0.0 to 1.0, validated)
  - matching_reasons: List[str]
  - location_distance_km: Optional[float]
  - days_since_report: Optional[int]
  - pet_name: Optional[str]
  - contact_available: bool
- [x] Create `MatchResult` model:
  - candidates: List[MatchCandidate]
  - top_match: Optional[MatchCandidate]
  - confidence_level: ConfidenceLevel
  - total_candidates_found: int
  - search_timestamp: str
- [x] Create `FinalOutput` model:
  - enriched_profile: dict
  - matches: MatchResult
  - explanation: str (min 20 characters)
  - recommended_actions: List[str]
  - confidence_summary: str
  - processing_metadata: dict

### 2.3 Mock Database & Data Access ✅
- [x] Create `data/mock_database.json` with:
  - 8 lost pet reports (various species, sizes, locations)
  - 5 sighting reports matching various lost pets
  - Realistic Costa Rica locations and descriptions
- [x] Create `src/utils/data_access.py`:
  - `MockDatabase` class with similarity scoring
  - `get_mock_database()` singleton function
  - `search_lost_pets()` search function
  - `search_sightings()` search function
  - `search_all_reports()` combined search
  - `_calculate_similarity()` simple scoring algorithm (temp)
  - `calculate_location_distance()` distance estimation
  - `calculate_days_since()` date utilities

### 2.4 Test Cases ✅
- [x] `examples/valid_case_1/` - Complete lost dog report
- [x] `examples/valid_case_2/` - Complete lost cat report
- [x] `examples/edge_case_1/` - Minimal information test
- [x] `examples/invalid_case_1/` - Missing required fields
- [x] `examples/invalid_case_2/` - Multiple validation violations
- [x] Each case includes test_case.json and README.md
- [x] Created `tests/test_phase1_2.py` validation script

---

## Phase 3: Utility Functions ✅ COMPLETED

### 3.1 Image Utilities (`/src/utils/image_utils.py`) ✅
- [x] Function: `validate_image_format(file_path: str) -> bool`
  - Check file exists and is valid image format (JPEG, PNG, GIF, BMP, WebP)
  - Validate file size (max 5MB)
- [x] Function: `resize_image_for_api(image_path: str, max_size: tuple) -> bytes`
  - Resize large images to reduce API costs
  - Convert to RGB and optimize
- [x] Function: `encode_image_to_base64(image_path: str) -> str`
  - Convert image to base64 for API calls
- [x] Function: `process_multiple_images(image_paths: List[str]) -> List[dict]`
  - Batch process multiple pet images
- [x] Additional utility functions implemented

### 3.2 Embedding Utilities (`/src/utils/embedding_utils.py`) ✅
- [x] Function: `create_pet_embedding(pet_data: PetDescription) -> List[float]`
  - Generate vector embedding from structured pet data
- [x] Function: `initialize_vector_store() -> VectorStore`
  - Set up ChromaDB
- [x] Function: `add_to_vector_store(pet_id: str, embedding: List[float], metadata: dict)`
  - Store pet report in vector database
- [x] Function: `search_vector_store(query_embedding: List[float], top_k: int = 5) -> List[dict]`
  - Query vector store for similar pets
- [x] Additional functions: cosine_similarity, batch_create_embeddings

---

## Phase 4: Agent Implementation ✅ COMPLETED

### 4.1 Visual & Text Extractor Agent (`/src/agents/visual_extractor_agent.py`) ✅
- [x] Set up agent class (VisualTextExtractorAgent)
- [x] Implement image-to-text vision model integration:
  - Uses GPT-4o Vision model
  - Extract: species, size, colors, distinctive features
- [x] Implement text processing:
  - Parse user description
  - Clean and normalize text
  - Extract location entities
- [x] Function: `analyze_images(images: List[str]) -> dict`
  - Process all images and combine insights
- [x] Function: `analyze_text(description: str) -> dict`
  - Parse free-text description
- [x] Function: `merge_and_validate(image_data: dict, text_data: dict, location: Location) -> PetDescription`
  - Combine multimodal data into validated Pydantic model
- [x] Add error handling for:
  - Invalid image formats
  - API failures
  - Missing critical information
- [x] Implement logging for all operations

### 4.2 Match & Similarity Agent (`/src/agents/similarity_agent.py`) ✅
- [x] Set up agent class (MatchSimilarityAgent)
- [x] Function: `generate_embedding(pet_profile: PetDescription) -> List[float]`
  - Create vector representation
- [x] Function: `search_with_embeddings(query_embedding) -> List[dict]`
  - Search using real embeddings
- [x] Function: `search_with_mock(query_pet) -> List[dict]`
  - Search using mock similarity
- [x] Function: `calculate_matching_reasons(query_pet: PetDescription, candidate: dict) -> List[str]`
  - Generate human-readable matching reasons
- [x] Function: `create_match_candidate(report, score, query_pet) -> MatchCandidate`
  - Create validated match candidates
- [x] Add distance calculation between locations
- [x] Return validated `MatchResult` model

### 4.3 Decision & Explanation Agent (`/src/agents/decision_agent.py`) ✅
- [x] Set up agent class (DecisionExplanationAgent)
- [x] Function: `should_notify_user(match: MatchCandidate) -> bool`
  - Apply business logic for notifications
- [x] Function: `generate_explanation(pet_profile: PetDescription, match: MatchCandidate) -> str`
  - Create natural language explanation for users
- [x] Function: `generate_recommendations(match_result, pet_profile) -> List[str]`
  - Generate actionable recommendations
- [x] Function: `create_confidence_summary(match_result) -> str`
  - Create confidence summary
- [x] Function: `process(pet_profile, match_result) -> FinalOutput`
  - Assemble complete user-facing response
- [x] Add logging for decision-making process

---

## Phase 5: Orchestration & Main Pipeline

### 5.1 Main Pipeline (`/src/main.py`)
- [ ] Import all agents and models
- [ ] Function: `load_config() -> dict`
  - Load environment variables
  - Initialize API clients
- [ ] Function: `setup_agents() -> tuple`
  - Initialize all three agents
  - Set up vector store connection
- [ ] Function: `process_pet_report(user_input: UserInput) -> FinalOutput`
  - Orchestrate sequential agent pipeline:
    1. Call Visual & Text Extractor Agent
    2. Call Match & Similarity Agent
    3. Call Decision & Explanation Agent
  - Handle errors at each stage
  - Log the entire pipeline flow
- [ ] Function: `main()`
  - Parse command-line arguments or config
  - Load example cases
  - Process reports
  - Display results
- [ ] Add comprehensive error handling
- [ ] Add performance timing/metrics

### 5.2 Agent Collaboration Flow
- [ ] Implement data passing between agents
- [ ] Validate intermediate outputs
- [ ] Add traceability (optional: Langfuse integration)
- [ ] Log each agent's contribution

---

## Phase 6: Test Cases & Examples

### 6.1 Valid Cases
- [ ] `examples/valid_case_1/`
  - Create sample dog images
  - Write description text file
  - Define expected output JSON
- [ ] `examples/valid_case_2/`
  - Create sample cat images
  - Write description text file
  - Define expected output JSON

### 6.2 Edge Cases
- [ ] `examples/edge_case_1/`
  - Single image with minimal description
  - Test agent's ability to extract from limited data

### 6.3 Invalid Cases
- [ ] `examples/invalid_case_1/`
  - Missing required location fields
  - Test validation error handling
- [ ] `examples/invalid_case_2/`
  - Corrupted image file
  - Test image processing error handling

### 6.4 Test Data for Vector Store
- [ ] Create 10-15 mock lost pet reports
- [ ] Create 5-10 mock sighting reports
- [ ] Populate vector store with test data
- [ ] Document expected matches

---

## Phase 7: Documentation

### 7.1 Proposal Document (`/docs/proposal.md`)
- [ ] **Problem Statement** (150+ words):
  - Describe limitations of current lost pet platforms
  - Explain why multi-agent approach is needed
  - Define user pain points
- [ ] **Solution Overview** (150+ words):
  - Explain multi-agent architecture
  - Describe each agent's role
  - Justify why single agent wouldn't work
- [ ] **Target Users**:
  - Pet owners
  - Public reporting sightings
  - Rescue organizations
- [ ] **Technology Stack**:
  - List all integrations (LangChain, Vector Store, Vision AI, Pydantic)
  - Justify each choice
- [ ] **Success Criteria** (5+ measurable outcomes):
  - Match accuracy ≥85%
  - Report completion improvement
  - User confidence metrics
  - False positive reduction
  - Response time benchmarks

### 7.2 Main README (`/README.md`)
- [ ] Project title and overview
- [ ] Features and capabilities
- [ ] Architecture diagram (text-based or image)
- [ ] Technology stack details
- [ ] Installation instructions:
  - Python version requirement
  - Virtual environment setup
  - Dependency installation
  - Environment variable configuration
- [ ] Usage instructions:
  - How to run the system
  - Example commands
  - Expected outputs
- [ ] Project structure explanation
- [ ] API keys and credentials setup
- [ ] Sample results and screenshots
- [ ] Future improvements
- [ ] License and contact info

### 7.3 Code Documentation
- [ ] Add docstrings to all functions (minimum 8 functions)
- [ ] Add type hints throughout codebase
- [ ] Add inline comments for complex logic
- [ ] Document agent prompts and reasoning

---

## Phase 8: Quality Assurance & Polish

### 8.1 Code Quality
- [ ] Review all type hints are present
- [ ] Ensure Pydantic validators work correctly
- [ ] Test error handling paths
- [ ] Remove hardcoded values
- [ ] Verify environment variables are used
- [ ] Clean up debug print statements
- [ ] Add proper logging levels

### 8.2 Testing
- [ ] Run all 5+ example cases
- [ ] Verify valid cases produce correct matches
- [ ] Verify edge cases are handled gracefully
- [ ] Verify invalid cases raise appropriate errors
- [ ] Test with different image formats (JPEG, PNG)
- [ ] Test with various description lengths

### 8.3 Performance
- [ ] Measure end-to-end processing time
- [ ] Optimize image processing if needed
- [ ] Check API rate limits and costs
- [ ] Document performance benchmarks

### 8.4 Security
- [ ] Verify no API keys in code
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Validate all user inputs
- [ ] Sanitize file paths

---

## Phase 9: Final Deliverables Checklist

### 9.1 Repository Contents
- [ ] Complete source code with proper structure
- [ ] All 3 agents implemented (`visual_extractor_agent.py`, `similarity_agent.py`, `decision_agent.py`)
- [ ] All Pydantic models with validators
- [ ] Minimum 8 well-named functions with type hints
- [ ] `main.py` with end-to-end orchestration
- [ ] `requirements.txt` with pinned versions
- [ ] `.env.example` template
- [ ] `.gitignore` properly configured

### 9.2 Documentation
- [ ] `proposal.md` (2-3 pages) with:
  - 150+ word problem statement
  - 150+ word solution overview
  - 5+ success criteria
- [ ] Comprehensive `README.md` with:
  - Installation instructions
  - Usage examples
  - Architecture explanation
  - Feature list

### 9.3 Examples
- [ ] 5+ test cases in `/examples` directory
- [ ] At least 2 valid cases
- [ ] At least 1 edge case
- [ ] At least 2 invalid cases
- [ ] Expected outputs documented

### 9.4 Technical Requirements
- [ ] Multi-agent system (3 agents minimum)
- [ ] LangChain integration for orchestration
- [ ] Vector Store (ChromaDB or FAISS) for similarity search
- [ ] Image-to-Text (Vision AI) integration
- [ ] Pydantic models with strict validation
- [ ] Environment variables only (no hardcoded keys)
- [ ] Error handling for all failure modes
- [ ] Logging throughout the system
- [ ] Type hints on all functions
- [ ] Sequential collaboration pattern (Agent 1 → 2 → 3)

---

## Phase 10: REST API for Web Integration

### 10.1 FastAPI Setup (`/src/api/main.py`)
- [ ] Install FastAPI and Uvicorn
- [ ] Create FastAPI application instance
- [ ] Configure CORS for web access
- [ ] Set up middleware for error handling
- [ ] Configure logging
- [ ] Add health check endpoint

### 10.2 API Endpoints (`/src/api/routes/`)
- [ ] **POST /api/v1/report/lost** - Submit lost pet report
  - Accept multipart/form-data (images + JSON)
  - Validate input using Pydantic models
  - Trigger agent pipeline
  - Return enriched profile and matches
- [ ] **POST /api/v1/report/sighting** - Submit sighting report
  - Same structure as lost pet endpoint
  - Search against lost pets database
- [ ] **GET /api/v1/search** - Search for matches
  - Query parameters: species, location, colors
  - Return matching reports
- [ ] **GET /api/v1/report/{report_id}** - Get report details
  - Return full report information
- [ ] **GET /api/v1/health** - Health check endpoint
  - Return API status and version

### 10.3 Request/Response Models (`/src/api/schemas.py`)
- [ ] `ReportRequest` schema for incoming requests
- [ ] `ReportResponse` schema for API responses
- [ ] `MatchResponse` schema for search results
- [ ] `ErrorResponse` schema for error handling
- [ ] Add examples and descriptions for API docs

### 10.4 File Upload Handling
- [ ] Function: `save_uploaded_images(files: List[UploadFile]) -> List[str]`
  - Save images to temporary directory
  - Validate file types (JPEG, PNG)
  - Limit file sizes (max 5MB per image)
  - Return list of saved file paths
- [ ] Function: `cleanup_temp_files(file_paths: List[str])`
  - Remove temporary files after processing
  - Handle cleanup errors gracefully

### 10.5 Async Processing
- [ ] Make agent pipeline async-compatible
- [ ] Use async database operations
- [ ] Implement background tasks for long-running operations
- [ ] Add request timeout handling

### 10.6 API Documentation
- [ ] Enable automatic OpenAPI/Swagger docs at `/docs`
- [ ] Add detailed endpoint descriptions
- [ ] Include request/response examples
- [ ] Document error codes and responses

### 10.7 Error Handling & Validation
- [ ] Global exception handler for unexpected errors
- [ ] Validation error handler for Pydantic errors
- [ ] HTTP status codes (400, 404, 422, 500)
- [ ] User-friendly error messages
- [ ] Log all errors with request context

### 10.8 Testing API (`/tests/test_api.py`)
- [ ] Test health endpoint
- [ ] Test lost pet report submission
- [ ] Test sighting report submission
- [ ] Test search endpoint
- [ ] Test file upload validation
- [ ] Test error handling
- [ ] Integration tests with mock agents

### 10.9 Deployment Preparation
- [ ] Create `run_api.py` script for starting server
- [ ] Add API configuration to .env
- [ ] Document API endpoints in README
- [ ] Create Postman/curl examples
- [ ] Add rate limiting (optional)

---

## Phase 11: Optional Enhancements

### 11.1 Monitoring (Langfuse)
- [ ] Integrate Langfuse for tracing
- [ ] Track agent performance metrics
- [ ] Monitor API costs
- [ ] Visualize decision flows

### 11.2 Additional Features
- [ ] Simple HTML/JavaScript frontend demo
- [ ] Database persistence (SQLite/PostgreSQL)
- [ ] Email/SMS notifications
- [ ] Multi-language support
- [ ] Real-time sighting updates via WebSockets
- [ ] Mobile app integration

### 11.3 Advanced Matching
- [ ] Time-based relevance scoring
- [ ] Geographic clustering
- [ ] Behavioral pattern analysis
- [ ] Breed-specific matching

### 11.4 Security Enhancements
- [ ] API key authentication
- [ ] Rate limiting per user/IP
- [ ] Input sanitization
- [ ] HTTPS enforcement

---

## Success Metrics

### Technical Metrics
- Match accuracy ≥85% on test cases
- End-to-end processing time < 30 seconds
- Zero crashes on invalid inputs
- All error cases handled gracefully

### Code Quality Metrics
- 100% type hint coverage
- Minimum 8 documented functions
- Zero hardcoded credentials
- Clean separation of concerns (agents, models, utils)

### Documentation Metrics
- Proposal meets word count requirements (150+ words per section)
- README is comprehensive and clear
- All examples runnable and documented
- Architecture clearly explained

---

## Timeline Estimate

- **Phase 1-2**: 1-2 days (Setup + Models) ✅ COMPLETED
- **Phase 3**: 1 day (Utilities)
- **Phase 4**: 3-4 days (Agents - most complex)
- **Phase 5**: 1-2 days (Orchestration)
- **Phase 6**: 1-2 days (Test cases)
- **Phase 7**: 1-2 days (Documentation)
- **Phase 8-9**: 1-2 days (QA + Final polish)
- **Phase 10**: 2-3 days (REST API for web integration)
- **Phase 11**: Optional (Enhancements as needed)

**Total: 12-18 days** (depending on experience level)
**Core functionality: 10-15 days** (Phases 1-9)
**With API: 12-18 days** (Phases 1-10)

---

## Notes & Considerations

1. **API Costs**: Vision AI APIs can be expensive. Use image resizing and caching to minimize costs.

2. **Vector Store Choice**: 
   - ChromaDB: Better for prototypes, easier setup
   - FAISS: Better performance, more complex setup

3. **LLM Selection**:
   - GPT-4 Vision: Best for image analysis
   - Claude 3: Good alternative with competitive pricing
   - Ensure model supports multimodal inputs

4. **Testing Strategy**: Start with mock data before using real API calls to save costs during development.

5. **Scalability**: Current design is proof-of-concept. For production, consider:
   - Async processing
   - Message queues
   - Distributed vector stores
   - Rate limiting

6. **Privacy**: Handle pet owner contact information securely. Don't log personal data.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limits | Implement retry logic with exponential backoff |
| Invalid images | Comprehensive validation before API calls |
| Vector store performance | Index optimization, limit search scope |
| Missing agent outputs | Validation between each agent step |
| API key exposure | Use .env files, never commit to git |
| Incomplete test data | Create diverse test cases early |

---

## Questions to Resolve Before Starting

1. Which LLM provider to use? (OpenAI, Anthropic, etc.)
2. Which vector store? (ChromaDB or FAISS)
3. Do we need Langfuse tracing? (Recommended but optional)
4. What's the budget for API calls during development?
## Ready to Start?

This implementation plan covers all requirements from the instructions:
- ✅ Multi-agent architecture (3 agents)
- ✅ LangChain integration
- ✅ Vector Store for similarity search
- ✅ Image-to-Text vision AI
- ✅ Pydantic models with validation
- ✅ 8+ well-named functions with type hints
- ✅ Proper repository structure
- ✅ 5+ example test cases
- ✅ Comprehensive documentation (proposal + README)
- ✅ Error handling and logging
- ✅ Environment variable configuration
- ✅ Success criteria and metrics
- ✅ REST API for web integration (Phase 10)

**Current Status**: Phase 1 & 2 COMPLETED ✅
**Next Steps**: Phase 3 (Utilities) → Phase 4 (Agents) → Phase 10 (API)
- ✅ Environment variable configuration
- ✅ Success criteria and metrics

**Next step**: Review this plan, make any adjustments, and then start with Phase 1!
