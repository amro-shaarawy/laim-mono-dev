# Product Requirements Document (PRD)

## 🧭 Product Overview

**Title**: Agentic AI Webapp for Real-Time Compliance Detection in Multilingual Board Meetings

**Description**:  
This web application provides real-time transcription of multilingual board meetings (Arabic/English) and automatically detects violations of ESG and compliance rules sourced from documents stored in Pinecone. The system displays alerts in real time, tagged by speaker and timestamp, and classifies uploaded compliance documents into categories for efficient semantic matching.

**Target Users**:  
Board members, compliance officers, ESG stakeholders, meeting auditors.

**Business Goals**:
- Reduce undetected regulatory violations in live discussions
- Simplify post-meeting auditing
- Enhance transparency and accountability in executive meetings


---

## 🎯 Goals & Success Metrics

### Primary Goals:
1. **Real-time, accurate transcription** of multilingual speech, including mixed Arabic-English code-switching.
2. **Instant violation detection** by semantically matching spoken content with ESG/Compliance documents.
3. **Speaker attribution and timestamping** for every flagged issue.
4. **Automatic classification** of uploaded documents for more accurate semantic search.
5. **Clear, high-signal UI alerts** with minimal disruption, tailored for board-level attention.

### Success Metrics:
- ≥95% transcription accuracy for code-switched Arabic-English conversations
- ≥90% precision and recall in flagging real violations (vs false positives/negatives)
- Alert latency < 2 seconds during live transcription
- ≥90% accuracy in document classification by category
- Positive feedback from ≥80% of test users (board members) on UX clarity and alert relevance

🔧 Functional Requirements
1. Multilingual Speech-to-Text (STT)
Transcribe audio input in real time from meetings

Support simultaneous Arabic and English, including intra-sentence language switching

Display transcription with speaker attribution and timestamps

2. Speaker Diarization
Identify individual speakers in real time

Maintain consistent speaker tags throughout session

Handle language change per speaker dynamically

3. Document Classification Engine
Automatically categorize uploaded regulation documents (e.g., ESG, Finance, Labor, Environmental, Ethics)

Store document metadata alongside embeddings in Pinecone

Support both manual override and batch classification

4. Compliance & ESG Risk Detection
Continuously scan live transcript

Perform semantic similarity checks between transcript and Pinecone vector DB

Detect potential violations and generate contextual matches

5. Real-Time Violation Alerts
Trigger warning popup with:

Speaker name or ID

Timestamp

Excerpt of offending sentence

Linked source document match (if applicable)

Include severity levels (info, moderate, critical)

6. Post-Meeting Analytics
Export violation reports

Summary per speaker

Highlighted heatmap of "risk moments"

Searchable transcript with violation markers

7. UX/Board-Friendly Interface
Minimal UI with clear font, dark mode, and large buttons

Interrupt only on meaningful alerts

Option to turn on/off live summary whisper panel
