# FL_04: Framing Your Work as Case Studies

**Author:** John Patrick Ilagan (Patrick)  
**Track:** AI Fluency Track: Week 2  
**Cohort:** FlyRank AI Backend Engineering Internship  

---

## 🎙️ Voice Card
> **Honest, Practical, Clear, Direct, Smooth, Friendly.**  
> *(No corporate buzzwords, no exaggerations, speaking like a builder talking to another builder.)*

---

## 🧩 Case 1: PrismLearning.AI (Interactive AI Learning Companion)

### Beat 1: The Problem
I struggle with reading long walls of text when learning complex technical concepts. Standard documentation and articles often feel overwhelming, and traditional AI chatbots tend to dump huge lectures back at you. I wanted a tool where learning felt like a live, back-and-forth conversation that kept me engaged rather than tired.

### Beat 2: What I Did & Decided
I built and shipped **PrismLearning.AI** in one week for an AMD Hackathon using **Next.js, TypeScript, Tailwind, and Zustand** on the frontend, with **Python, FastAPI, and Supabase** on the backend, running open-source models (Gemma & GPT-OSS) via **Fireworks AI**.
- **The Prompt Constraint**: I engineered the system prompt to strictly restrict response lengths and break any topic into 3 to 5 interactive, bite-sized steps instead of long summaries.
- **Multi-Source Extraction**: Built ingestion pipelines using pdfplumber, python-pptx, and youtube-transcript-api to extract content directly from decks, PDFs, and video links into interactive Mermaid.js diagrams.
- **The Deliberate Cut**: Because of the 1-week time constraint, I intentionally cut real-time live voice calls to focus entirely on reliable document processing, gamified quiz exports, and a vibrant mascot UI (Prism) that made learning feel approachable.

### Beat 3: What Came of It & What I Learned
The app is a working, deployed prototype that I actually use when exploring new topics. 
- **The Honest Wrinkle**: Some AI edge-case responses and summarizations still need prompt tuning and polishing.
- **The Real Takeaway**: I learned the danger of building on pure adrenaline without a locked spec. Thinking up ideas mid-build led to scope creep. It taught me that disciplined planning, a clear problem definition, and strict feature boundaries matter just as much as coding speed.

---

## ⚙️ Case 2: In-Memory Task Management CRUD API

### Beat 1: The Problem
Before this build, I had generated FastAPI backends with AI without deeply understanding the raw plumbing underneath. When something broke or returned an unexpected status code, I was guessing instead of debugging. I needed to build a REST API completely by hand from scratch to master HTTP mechanics, routing, and defensive validation.

### Beat 2: What I Did & Decided
Built an in-memory REST API in **Python 3.11** using **FastAPI and Uvicorn**, following a strict 6-stage development flow.
- **Full CRUD Lifecycle**: Hand-wrote endpoints for GET, POST, PUT, and DELETE with defensive request body validation (400 Bad Request) and missing ID handling (404 Not Found).
- **Filters & Compute**: Designed query parameters for completion filtering (?done=true) and case-insensitive search (?search=...), plus on-the-fly memory statistics calculation (GET /stats).
- **Interactive Documentation**: Configured OpenAPI documentation at /docs with grouped tags, summaries, and endpoint docstrings.

### Beat 3: What Came of It
- The API is fully tested via curl and Swagger UI, recorded across atomic Git stage commits on GitHub.
- **The Takeaway**: Stepping away from blind AI generation gave me complete intuition for HTTP status codes, request/response cycles, and why in-memory state loss on reboot necessitates database persistence.

---

## 👤 Bio Copy (About Patrick)

> Hey, I'm **Patrick (John Patrick Ilagan)**, a second-year BSIT student and Backend AI Engineering Intern at FlyRank AI. 
> 
> I specialize in **AI product prototyping**: turning defined product ideas into functional, deployed MVPs using AI-assisted development. I don't pretend to be a 10-year veteran. I'm a fast, curious junior builder who pairs with modern AI tooling to explore architectures, write clean APIs, build interactive interfaces, and test ideas in days instead of months.

---

## 📬 Contact & Call to Action (CTA)

> **Looking for a junior builder who can rapidly prototype your next AI feature or MVP?**  
> Let's talk about how I can help your team ship faster as a paid AI development intern.

---

## ⚖️ Before vs. After: The Voice Comparison

| 🤖 Before (Generic AI Sludge) | 👤 After (Patrick's Edited Authentic Voice) |
| :--- | :--- |
| *"Leveraged cutting-edge generative AI paradigms and state-of-the-art frameworks to architect a revolutionary gamified educational platform that maximizes user engagement and streamlines pedagogical outcomes."* | *"I struggle with reading long walls of text when learning. I built PrismLearning.AI to break complex topics into 3 to 5 interactive, conversational steps with an inviting mascot UI so learning actually feels fun."* |
