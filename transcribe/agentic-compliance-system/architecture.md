
# 🧱 System Architecture Document – Agentic AI Compliance System

**Owner**: شعراوي  
**Role**: System Architect (Omar)  
**Version**: 1.0  
**Date**: July 2025

---

## 1. 🎯 System Purpose

The system provides real-time, offline-capable transcription and regulatory compliance monitoring for board-level conversations. It detects potential legal/policy violations based on stored documents and delivers immediate alerts via a lightweight web interface.

---

## 2. 🧩 System Components

### 🧠 CrewAI Agents

| Agent Name            | Role                                                                       |
|-----------------------|----------------------------------------------------------------------------|
| `AudioIngestAgent`    | Captures live audio, slices into small time chunks                         |
| `TranscriberAgent`    | Uses Whisper-Turbo-v3 to convert audio to multilingual text                |
| `DiarizationAgent`    | Assigns speaker IDs via pyannote or resemblyzer                            |
| `ComplianceAgent`     | Matches transcript to embedded regulation documents in Pinecone            |
| `AlertAgent`          | Formats and emits popup alert messages                                     |
| `ClassifierAgent`     | Tags new documents with categories before embedding                        |
| `EmbedderAgent`       | Embeds documents into vector form and uploads to Pinecone                  |
| `FrontendBridgeAgent` | Connects backend agents with frontend for live updates and reports         |

---

## 3. 🔁 Data Flow

```
[Audio Stream]
  → AudioIngestAgent
    → TranscriberAgent (Whisper-Turbo)
      → DiarizationAgent
        → ComplianceAgent
          → Pinecone Vector Search
            ↳ Violation
              → AlertAgent
                → FrontendBridgeAgent → UI Popup

[Document Upload]
  → ClassifierAgent
    → EmbedderAgent → Pinecone Upsert
```

---

## 4. 🏗️ Technology Stack

| Layer              | Stack/Tech                                                     |
|--------------------|----------------------------------------------------------------|
| Transcription      | Whisper-Turbo-v3 (offline)                                     |
| Diarization        | pyannote-audio / resemblyzer                                  |
| Embedding Model    | BGE-Base / Instructor / MiniLM                                 |
| Vector DB          | Pinecone (cloud API)                                           |
| Classification     | Scikit-learn / SetFit                                          |
| Backend            | Python + FastAPI / Flask + CrewAI agent orchestration          |
| Frontend           | React / Streamlit (with WebSocket or polling updates)         |
| Storage / Config   | Pinecone credentials in `.env`, optional SQLite/Redis cache    |

---

## 5. ⚠️ Alerts & Interface

- **Format**: Popup toasts (top-right)
- **Triggers**: Similarity > threshold (e.g., cosine > 0.85)
- **Details**: Speaker ID, timestamp, violation summary, severity color
- **Actions**: Click to view full transcript context

---

## 6. 🔐 Security & Operations

- Pinecone API secured via token and HTTPS  
- No user data stored unless explicitly enabled  
- Retry and logging middleware on API calls  
- Optional support for local/offline fallback in future

---

## ✅ End of Architecture Document
