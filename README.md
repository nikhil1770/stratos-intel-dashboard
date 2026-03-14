# 🌐 STRATOS_INTEL

**Stratos Intel** is a high-performance Cyber-Intelligence Dashboard designed for real-time global monitoring. It aggregates, processes, and visualizes geopolitical data streams, sentiment shifts, and localized intelligence pings across a hyper-modern 3D WebGL interface.

---

## 🚀 Key Features

*   **3D Global Visualization**: Dynamic Three.js-powered globe with real-time sentiment tinting and atmospheric scattering.
*   **Multi-Source Data Ingestion**: Automated harvesters for GDELT, RSS feeds, and Mastodon social streams.
*   **NLP Intelligence Layer**: Advanced topic classification (Politics, Tech, AI, Finance, etc.) and sentiment analysis using Python.
*   **Interactive Hot Zones**: Real-time tracking of high-activity regions with predictive "Active Hot Zones" analytics.
*   **Local Interceptor**: A dedicated terminal-style feed for granular social pings and raw intelligence intercepts.
*   **Stratos Design System**: A premium, glassmorphism-inspired UI with custom neon-border architecture and OKLCH color variables.

---

## 🛠️ Technology Stack

*   **Frontend**: HTML5, Vanilla CSS (OKLCH Vars), Javascript (ES6+)
*   **3D/Maps**: Globe.gl, Three.js, Leaflet.js
*   **Backend**: FastAPI (Python), Uvicorn
*   **Processing**: Python (NLP), Regular Expressions, Sentiment Analysis
*   **Database**: SQLAlchemy, PostgreSQL / SQLite
*   **Geospatial**: GeoJSON, Nominatim API

---

## 📝 Setup and Installation

### 1. Prerequisites
- Python 3.9+
- Pip / Virtualenv
- A running PostgreSQL or SQLite environment

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python reset_db.py
```

### 4. Launch Ingestion Layers
Start the collectors and processors in separate terminals:
```bash
python ingestion/mastodon_client.py
python ingestion/rss_client.py
python processing/nlp_processor.py
```

### 5. Start the Web Server
Launch the FastAPI core:
```bash
python main.py
```
Access the dashboard at `http://localhost:8000`.

---

## 📂 Project Structure

- `/frontend`: HTML, CSS, and `app.js` (Globe + UI Logic).
- `/ingestion`: Python harvesters for GDELT, RSS, and Mastodon.
- `/processing`: NLP classification and database workers.
- `/database`: SQLAlchemy models and schema definitions.
- `main.py`: The FastAPI application entry point.

---

## 🛡️ License
Proprietary Intelligence Core - STRATOS_INTEL.
