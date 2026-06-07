# 🎓 AI Timetable RAG Assistant

An AI-powered College Timetable Assistant built using **Python, ChromaDB, Sentence Transformers, Groq LLM, and Streamlit/Gradio UI**.

The system can answer:

* Teacher details
* Timetable questions
* Subject schedules
* Class timings
* Faculty information
* Free periods
* Room allocations
* Semantic college queries

using **RAG (Retrieval Augmented Generation)** architecture.

---

# 🚀 Features

## ✅ Timetable Question Answering

Examples:

* Who teaches DBMS?
* What subject is scheduled for CSE-B Tuesday period 6?
* Who is handling ECE-A Monday 1st period?
* Give me Dr. Sanjay Pillai timetable

---

## ✅ Faculty Information Retrieval

Examples:

* Teacher phone numbers
* Teacher email IDs
* Qualifications
* Research details
* Achievements
* Specializations
* Free periods

---

## ✅ Semantic Search using Vector Database

The system uses:

* Sentence Transformers embeddings
* ChromaDB vector database

to find semantically similar information.

---

# 🧠 Architecture

## Overall Flow

```text
User Question
      ↓
Embedding Generation
      ↓
Semantic Search in ChromaDB
      ↓
Relevant Context Retrieval
      ↓
LLM (Groq / Gemini)
      ↓
Final AI Response
```

---

# 📦 Technologies Used

| Technology            | Purpose              |
| --------------------- | -------------------- |
| Python 3.11           | Backend              |
| ChromaDB              | Vector Database      |
| Sentence Transformers | Embedding Generation |
| Groq API              | LLM Inference        |
| Streamlit / Gradio    | UI                   |
| PyPDF                 | PDF Extraction       |
| JSON                  | Timetable Storage    |

---

# 📚 Libraries Used

```txt
langchain==0.2.0
langchain-community==0.2.0
langchain-groq==0.1.5
chromadb==0.5.0
sentence-transformers==2.7.0
pypdf==4.0.0
python-dotenv==1.0.0
tqdm==4.66.0
```

---

# 🗂️ Project Structure

```text
timetable-rag/
│
├── data/
│   ├── cse_timetable.json
│   ├── ece_timetable.json
│   ├── eee_timetable.json
│   ├── mech_timetable.json
│   └── teacher_biodata.pdf
│
├── src/
│   ├── timetable_rag.py
│   ├── app.py
│   └── streamlit_app.py
│
├── storage/
│   └── chroma_db/
│
├── requirements.txt
├── .env
└── README.md
```

---

# 🔍 What is RAG?

RAG stands for:

```text
Retrieval Augmented Generation
```

Instead of training an AI model with college data,
we:

1. Store data in a vector database
2. Retrieve relevant information
3. Send only relevant context to the LLM
4. Generate accurate answers

This improves:

* accuracy
* speed
* scalability
* dynamic data handling

---

# 🧬 Embedding Model

The project uses:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers.

Purpose:

* Convert text into vectors
* Enable semantic similarity search

Example:

```text
"Who teaches DBMS?"
```

and

```text
"DBMS faculty"
```

become similar vectors.

---

# 🗄️ ChromaDB Usage

ChromaDB is used as a local persistent vector database.

It stores:

* teacher embeddings
* timetable embeddings
* metadata
* document chunks

Data remains saved even after restarting the app.

---

# 📑 Collections Used

## 1. Teacher Collection

Stores:

* name
* email
* phone
* qualification
* specialization
* achievements
* free periods

---

## 2. Timetable Collection

Stores:

* section
* day
* period
* subject
* teacher
* room

Each timetable entry becomes a searchable chunk.

---

# ⚙️ Hybrid Search System

The project uses two approaches:

## ✅ Exact Structured Search

Used for:

* Monday period 3
* CSE-A Tuesday period 6
* Room lookup

Uses:

* metadata filtering
* Python logic

---

## ✅ Semantic AI Search

Used for:

* teacher details
* achievements
* qualifications
* research
* general queries

Uses:

* embeddings
* vector similarity
* LLM reasoning

---

# 🧱 Chunking Strategy

## Teacher Chunks

Example:

```text
Teacher Name: Ms. Kavitha Nair
Department: CSE
Subjects: DBMS
Phone: +91 XXXXX
Free Periods: Monday Period 3
```

---

## Timetable Chunks

Example:

```text
Section: CSE-B
Day: Tuesday
Period: 6
Subject: Maths
Teacher: Mr. Suresh Babu
Room: CS-102
```

---

# 🖥️ UI

The project supports:

* Streamlit UI
* Gradio UI
* Terminal Chat Interface

---

# 🔐 Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_api_key
```

---

# ▶️ How to Run

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

---

## Run Terminal App

```bash
python src/app.py
```

---

## Run Streamlit UI

```bash
streamlit run src/streamlit_app.py
```

---

# 🧠 Example Questions

```text
Who teaches DBMS?
```

```text
What subject is scheduled for CSE-B Tuesday period 6?
```

```text
Give me Dr. Sanjay Pillai details
```

```text
Who is free on Monday period 3?
```

```text
What is the room for ECE-A Monday 1st period?
```

---

# ⚠️ Challenges Faced

## Token Limit Errors

Large prompts caused:

```text
413 Request Too Large
```

Solution:

* reduced retrieved chunks
* hybrid filtering approach

---

## Semantic Retrieval Issues

Timetable queries are structured data.

Solution:

* added metadata filtering
* exact search logic

---

## PDF Extraction Problems

Teacher biodata format was inconsistent.

Solution:

* custom regex extraction logic

---

# 🚀 Future Improvements

* Attendance integration
* Faculty login
* Student portal
* Voice assistant
* WhatsApp bot
* Mobile app
* Real-time timetable updates
* Multi-college support
* OCR timetable upload

---

# 👨‍💻 Developed By

Anil Kumar
Computer Science Engineering Student

---

# 📌 Conclusion

This project demonstrates:

* RAG architecture
* Vector databases
* Semantic search
* LLM integration
* Hybrid AI systems
* Real-world AI application development

for educational timetable management systems.
