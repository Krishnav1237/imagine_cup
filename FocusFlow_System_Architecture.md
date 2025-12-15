# FocusFlow – System Architecture

## 1. Overview
FocusFlow is an ADHD-focused, attention-adaptive learning platform that ingests long-form educational content and converts it into personalized short-form learning units using AI. The system is designed with privacy-first camera-based attention tracking, modular AI services, and scalable cloud infrastructure.

---

## 2. High-Level Architecture

```
Client (Web / Mobile)
│
├── UI Layer (Next.js / React Native)
│   ├── Video Player
│   ├── Camera & Attention Tracker (On-device)
│   ├── Notes & Quiz UI
│
├── API Gateway
│   ├── Authentication
│   ├── Rate Limiting
│   └── Request Routing
│
├── Backend Services (FastAPI)
│   ├── Content Ingestion Service
│   ├── Transcription Service
│   ├── AI Processing Service
│   ├── Personalization Engine
│   └── Analytics Service
│
├── AI Layer
│   ├── LLMs (Summarization & Adaptation)
│   ├── Speech-to-Text Models
│   └── Embedding Models
│
├── Data Layer
│   ├── PostgreSQL
│   ├── Vector Database
│   ├── Redis Cache
│   └── Object Storage
│
└── Monitoring & Analytics
```

---

## 3. Frontend Architecture

### 3.1 Web Client
- **Framework:** Next.js (React)
- **Styling:** Tailwind CSS + ShadCN UI
- **State Management:** Zustand
- **Data Fetching:** TanStack Query
- **Video:** Video.js + YouTube IFrame API
- **Camera Tracking:** MediaPipe + TensorFlow.js (on-device only)

### 3.2 Mobile Client
- **Framework:** React Native (Expo)
- **ML Acceleration:** CoreML (iOS), NNAPI (Android)

---

## 4. Backend Architecture

### 4.1 API Layer
- **Framework:** FastAPI
- **Auth:** Auth0 / Clerk
- **Gateway:** NGINX + Cloudflare

### 4.2 Core Services

#### Content Ingestion Service
- Handles YouTube URLs and file uploads
- Tools: yt-dlp, pdfplumber, python-pptx, python-docx

#### Transcription Service
- Whisper (large-v3) or Faster-Whisper
- Converts audio to timestamped text

#### AI Processing Service
- Chunking and summarization
- Concept dependency extraction
- Framework: LangChain / LlamaIndex

#### Personalization Engine
- Adjusts chunk size, density, and pacing
- Inputs: attention metrics, interaction data
- Outputs: adaptive learning parameters

---

## 5. AI & ML Architecture

### 5.1 Language Models
- **Primary (Cloud):** GPT-4.x
- **Secondary (Self-hosted):** LLaMA 3 / Mistral

### 5.2 Vision Models
- MediaPipe Face Mesh
- Eye gaze & head pose estimation
- Runs strictly on-device

### 5.3 Embeddings & Retrieval
- Sentence transformers
- Vector DB: Qdrant / Pinecone

---

## 6. Data Architecture

### 6.1 Databases
- **PostgreSQL:** Users, sessions, content metadata
- **Redis:** Session state, real-time attention windows
- **Vector DB:** Semantic search & recall

### 6.2 Object Storage
- S3 / Cloudflare R2
- Stores transcripts and processed content

---

## 7. Privacy & Security Architecture

- Camera processing is local-only
- No raw video frames stored
- Explicit per-session consent
- GDPR-ready data controls
- Encryption at rest and in transit

---

## 8. Deployment & Infrastructure

- **Cloud:** AWS / GCP (India region)
- **Containers:** Docker
- **Orchestration:** Kubernetes (scaling phase)
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus, Grafana, Sentry

---

## 9. Scalability Strategy

- Async task queues (Celery / Temporal)
- Horizontal scaling for AI services
- Model abstraction layer for vendor independence

---

## 10. Summary

The FocusFlow architecture prioritizes:
- ADHD-first UX
- Privacy-by-design
- Modular AI services
- Cost-efficient scalability

This design supports rapid MVP development while remaining production-ready for large-scale deployment.
