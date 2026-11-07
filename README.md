# CartMind — Agentic AI E-Commerce Shopping & Feedback Intelligence

A production-grade **Agentic AI** shopping assistant built with **LangChain**, **Google Gemini**, and a high-fidelity **FastAPI** backend.

**CartMind is architected around two core mission pillars:**
1. **Intelligent Customer Query Clarification & Exploration:** Translates conversational shopping queries into structured API tool calls, strictly enforcing hard customer constraints (budget ceilings, sizing, brand, color, stock availability) and generating side-by-side Markdown comparison tables.
2. **Review & Feedback Sentiment Analysis Engine:** Evaluates customer reviews and app feedback using a LangGraph sentiment pipeline, extracting nuanced user sentiments (pros, cons, sentiment polarity, sarcasm detection) to generate evidence-backed replies and automated support escalations.

---

## 1. System Architecture

```text
                               +-----------------------------+
                               |     User Shopping Query     |
                               +--------------+--------------+
                                              |
                                              v
                               +-----------------------------+
                               |     Conversational CLI      |
                               |       (run_agent.py)        |
                               +--------------+--------------+
                                              |
                                              v
+------------------------------------------------------------------------------------------+
| LangChain ReAct Agent (app/agent.py)                                                     |
|                                                                                          |
|   1. Query Understanding & Constraint Extraction (Hard vs Soft constraints)              |
|   2. Model: Google Gemini Flash (ChatGoogleGenerativeAI)                                 |
|   3. Tool-Calling ReAct Loop (Reason -> Action -> Observation -> Final Answer)           |
|   4. Dynamic Synthesis: Markdown Comparison Table (>=2 products) or Single Recommendation|
+---------------------------------------------+--------------------------------------------+
                                              |
                                              v
+------------------------------------------------------------------------------------------+
| LangChain Tools (app/tools.py) & HTTP Client (app/api_client.py)                         |
|                                                                                          |
|   - search_products: Multi-token keyword search, budget, rating, color/size filtering   |
|   - get_product_catalogue: Full catalogue browsing & pagination                          |
|   - get_product_details: Deep specifications by product_id                               |
|   - get_product_pricing: Transparent selling price, original price, discount %           |
|   - get_customer_reviews: Authentic reviews, ratings, user comments                     |
|   - get_product_availability: Real-time inventory status, units, sizes, colors           |
+---------------------------------------------+--------------------------------------------+
                                              | HTTP GET
                                              v
+------------------------------------------------------------------------------------------+
| FastAPI E-Commerce Backend (app/main.py) [Port 8000]                                     |
|                                                                                          |
|   - GET /api/search                     - GET /api/products                              |
|   - GET /api/products/{id}              - GET /api/products/{id}/price                   |
|   - GET /api/products/{id}/reviews      - GET /api/products/{id}/availability            |
+------------------------------------------------------------------------------------------+
```

---

## 2. API-to-Tool Mapping

The LangChain tools map directly to the authoritative FastAPI backend endpoints:

| LangChain Tool | Backend Endpoint | HTTP Method | Key Arguments | Purpose |
| :--- | :--- | :---: | :--- | :--- |
| `search_products` | `/api/search` | `GET` | `query`, `category`, `brand`, `min_price`, `max_price`, `min_rating`, `available_only`, `sort_by`, `preferred_color`, `preferred_size` | Primary tool for finding products matching criteria and natural language queries. |
| `get_product_catalogue` | `/api/products` | `GET` | `category`, `brand`, `min_price`, `max_price`, `min_rating`, `keyword`, `skip`, `limit` | Browse general catalogue or paginated categories without free-text query. |
| `get_product_details` | `/api/products/{product_id}` | `GET` | `product_id` | Deep specifications, materials, and description of a known item. |
| `get_product_pricing` | `/api/products/{product_id}/price` | `GET` | `product_id` | Authoritative selling price, original price, discount %, and currency. |
| `get_customer_reviews` | `/api/products/{product_id}/reviews` | `GET` | `product_id`, `min_rating`, `limit` | Authentic customer reviews to extract verified pros and cons. |
| `get_product_availability` | `/api/products/{product_id}/availability` | `GET` | `product_id` | Verify stock inventory (`in_stock`, `low_stock`, `out_of_stock`), sizes, and colors. |
| `analyze_product_sentiment` | `/api/products/{product_id}/sentiment` | `GET` | `product_id` | Deep sentiment and sarcasm analysis across customer reviews with tone calibration. |
| `escalate_to_human_support` | `/api/support/escalate` | `POST` | `issue_summary`, `category`, `urgency`, `customer_query`, `product_id` | Seamless Human-in-the-Loop handover and authoritative support ticket generation. |



---

## 3. Gemini Model Configuration & Availability

We verified the Google Gemini model catalog against live API keys:
- **`gemini-3.5-flash-lite` (Active & Verified Default):** Verified operational with `200 OK` and sub-3-second tool-calling performance.
- **`gemini-3-flash-preview` (Alternative Available):** Verified operational with `200 OK`.
- **`gemini-3.8-flash` / `gemini-3.7-flash` / `gemini-3.6-flash`:** Officially registered in the Gemini API catalog, but currently returning `503 Service Unavailable (High demand)` on Google's free-tier servers.

The model is **fully configurable** in `.env` without modifying any agent code:
```dotenv
GEMINI_MODEL=gemini-3.5-flash-lite
```
*(You can switch to `gemini-3.8-flash` as soon as Google's regional demand spike clears).*

---

## 4. Setup & Installation

### Prerequisites
- Python 3.11+ (tested on Python 3.13)
- Google Gemini API Key

### Step 1: Virtual Environment Setup
```powershell
# Navigate to the project directory
cd mock-ecommerce-api

# Activate your virtual environment
..\myvenv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Ensure your `.env` contains:
```dotenv
GOOGLE_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
FASTAPI_BASE_URL=http://127.0.0.1:8000
AGENT_MAX_ITERATIONS=8
API_TIMEOUT_SECONDS=15
```

---

## 5. Execution Instructions

### Step 1: Start the Backend Service
Start the FastAPI server in one terminal:
```bash
uvicorn app.main:app --reload --port 8000
```
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### Step 2: Launch the Conversational Agent (CLI)
In a second terminal, launch the interactive agent CLI:
```bash
python run_agent.py
```

### Step 3: Launch the Streamlit Web UI (Browser)
Alternatively or alongside the CLI, launch the full-featured interactive web application:
```bash
streamlit run streamlit_app.py
```
- **Local Web UI:** `http://localhost:8501`
- **Features Included:**
  - 🎨 **Dark-Mode Modern Design System** with custom typography, badges, and smooth hover states.
  - ⚡ **Quick Prompt Shortcuts** for instant 1-click test queries (Belts under ₹1000, Running shoes comparison, RFID Wallets, etc.).
  - 📦 **Live Catalogue Browser** in sidebar with category filtering, prices, discount badges, and stock badges.
  - 🔍 **Live Backend Health Checker** displaying connected catalogue size and review counts.
  - 🤖 **Interactive Chat** with response generation timing, markdown table rendering, and conversation history.

---

## 6. Running Automated Tests

Run the full pytest suite (including backend unit tests, tool mapping tests, agent evaluation tests, and Playwright browser integration tests):

```bash
pytest -v
```

**Results (100% Passing):**
```text
============================= 65 passed in 13.22s =============================
- 30 Backend API & parameter parsing tests: PASSED
- 17 Sentiment & Sarcasm analysis tests: PASSED
- 10 LangChain Tool mapping & error handling tests: PASSED
- 7 Agent constraint & table formatting tests: PASSED
- 1 Playwright Swagger UI browser test: PASSED
```

---

## 7. Example Shopping Queries & Output

### Query: Multi-Attribute Discovery
> **User >** "Find comfortable black shoes under ₹3,000 with at least a 4-star rating."

**Assistant Response:**
```markdown
I found 2 shoes matching your criteria of black shoes under ₹3,000 with a 4-star or higher rating.

### Comparison Table

| Product | Price (INR) | Rating | Availability | Key Pros (from specs/reviews) | Key Cons (from specs/reviews) |
|---|---|---|---|---|---|
| **Puma Air Stride Lightweight Running Shoes**<br>*(PROD007)* | ₹2,699 <br>*(Orig. ₹4,499 - 40% off)* | 4.5 / 5 <br>(4 reviews) | In Stock <br>(18 units, Sizes: 7-11) | • Extremely lightweight and breathable mesh upper<br>• Responsive EVA foam cushioning & shock absorption<br>• Great arch support for gym & daily running | • Snug fit; users with wide feet recommend sizing up |
| **Bata Oxford Handcrafted Formal Derby Leather Shoes**<br>*(PROD008)* | ₹2,449 <br>*(Orig. ₹3,499 - 30% off)* | 4.5 / 5 <br>(3 reviews) | Low Stock <br>(3 units, Sizes: 7-10) | • Polished calfskin leather with a rich gloss finish<br>• Cushioned insoles and anti-skid rubber heels<br>• Excellent comfort for long office days & formal wear | • Requires a couple of days of breaking in<br>• Limited stock remaining (3 units) |

---

### Top Recommendation
* **For Running & Athletic Wear:** **Puma Air Stride Lightweight Running Shoes (PROD007)** is our top pick. Priced at **₹2,699**, it offers excellent cushioning and breathable mesh, backed by customer reviews praising its shock absorption.
* **For Formal & Office Wear:** **Bata Oxford Handcrafted Formal Derby Leather Shoes (PROD008)** at **₹2,449** is an exceptional leather option with padded inner soles.
```

---

## 8. Troubleshooting

1. **`UnicodeEncodeError: 'charmap' codec can't encode character '\u20b9'`:**
   - Windows PowerShell console default encoding is `cp1252`.
   - `run_agent.py` automatically configures UTF-8 encoding via `sys.stdout.reconfigure(encoding='utf-8')`.
2. **`Could not connect to FastAPI backend at http://127.0.0.1:8000`:**
   - Start the backend server before launching the agent: `uvicorn app.main:app --port 8000`.
3. **`503 Model is currently experiencing high demand`:**
   - Google Gemini free tier can experience demand spikes on specific model endpoints (like 3.8/3.7).
   - Change `GEMINI_MODEL=gemini-3.5-flash-lite` or `gemini-3-flash-preview` in `.env`.
