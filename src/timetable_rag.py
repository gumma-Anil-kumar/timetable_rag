
import os
import json
import re

import pypdf
import chromadb

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from chromadb.api.types import Documents, Embeddings
from chromadb import EmbeddingFunction
from groq import Groq

load_dotenv()

os.environ["ANONYMIZED_TELEMETRY"] = "False"


# =========================================================
# EMBEDDING FUNCTION
# =========================================================

class MiniLMEmbedder(EmbeddingFunction):

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def __call__(self, input: Documents) -> Embeddings:

        return self.model.encode(input).tolist()


# =========================================================
# MAIN RAG CLASS
# =========================================================

class TimetableRAG:

    def __init__(self):

        print("Loading embedding model...")

        self.embedder = MiniLMEmbedder()

        print("Initializing ChromaDB...")

        self.chroma_client = chromadb.PersistentClient(
            path="./storage/chroma_db"
        )

        # =====================================================
        # COLLECTIONS
        # =====================================================

        try:

            self.teacher_collection = (
                self.chroma_client.get_collection(
                    name="teachers",
                    embedding_function=self.embedder
                )
            )

        except:

            self.teacher_collection = (
                self.chroma_client.create_collection(
                    name="teachers",
                    embedding_function=self.embedder
                )
            )

        try:

            self.timetable_collection = (
                self.chroma_client.get_collection(
                    name="timetables",
                    embedding_function=self.embedder
                )
            )

        except:

            self.timetable_collection = (
                self.chroma_client.create_collection(
                    name="timetables",
                    embedding_function=self.embedder
                )
            )

        # =====================================================
        # GROQ
        # =====================================================

        self.groq_client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.timetable_data = {}
        self.teachers_data = []

    # =========================================================
    # LOAD JSON
    # =========================================================

    def load_timetable_json(self, path):

        with open(path, "r", encoding="utf-8") as f:

            data = json.load(f)

        department = data.get(
            "department",
            "Unknown"
        )

        sections = data.get(
            "sections",
            {}
        )

        for section_name, section_data in sections.items():

            section_data["department"] = department

            self.timetable_data[
                section_name
            ] = section_data

        print(
            f"Loaded {len(sections)} sections from {path}"
        )

    # =========================================================
    # EXTRACT TEACHERS
    # =========================================================

    def extract_teachers_from_pdf(self, pdf_path):

        teachers = []

        with open(pdf_path, "rb") as f:

            reader = pypdf.PdfReader(f)

            full_text = ""

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    full_text += text + "\n"

        blocks = re.split(
            r'\n\s*(?=\d+\.\s)',
            full_text
        )

        for block in blocks:

            block = block.strip()

            if not block:
                continue

            if "Employee ID" not in block:
                continue

            teacher = {}

            # =================================================
            # NAME
            # =================================================

            name_match = re.search(
                r'\d+\.\s+([^\n]+)',
                block
            )

            if not name_match:
                continue

            teacher["name"] = (
                name_match.group(1).strip()
            )

            # =================================================
            # FIELD EXTRACTOR
            # =================================================

            def get_field(label):

                pattern = (
                    rf'{label}:\s*(.+?)'
                    rf'(?=\n\s*[A-Z][a-zA-Z ]+:|$)'
                )

                match = re.search(
                    pattern,
                    block,
                    re.DOTALL
                )

                if match:

                    return (
                        match.group(1)
                        .replace("\n", " ")
                        .strip()
                    )

                return ""

            teacher["employee_id"] = (
                get_field("Employee ID")
            )

            teacher["office"] = (
                get_field("Office")
            )

            teacher["department"] = (
                get_field("Department")
            )

            teacher["experience"] = (
                get_field("Experience")
            )

            teacher["phone"] = (
                get_field("Phone")
            )

            teacher["qualification"] = (
                get_field("Qualification")
            )

            teacher["email"] = (
                get_field("Email")
            )

            teacher["specialization"] = (
                get_field("Specialization")
            )

            teacher["subjects"] = (
                get_field("Subjects Taught")
            )

            teacher["research"] = (
                get_field("Research")
            )

            teacher["achievements"] = (
                get_field("Achievements")
            )

            teacher["free_periods"] = (
                get_field("Free Periods")
            )

            teachers.append(teacher)

        self.teachers_data = teachers

        print(
            f"Extracted {len(teachers)} teachers"
        )

    # =========================================================
    # TEACHER TEXT
    # =========================================================

    def teacher_to_text(self, teacher):

        return (
            f"Teacher Name: {teacher.get('name', '')}\n"
            f"Employee ID: {teacher.get('employee_id', '')}\n"
            f"Department: {teacher.get('department', '')}\n"
            f"Phone: {teacher.get('phone', '')}\n"
            f"Email: {teacher.get('email', '')}\n"
            f"Office: {teacher.get('office', '')}\n"
            f"Qualification: {teacher.get('qualification', '')}\n"
            f"Specialization: {teacher.get('specialization', '')}\n"
            f"Experience: {teacher.get('experience', '')}\n"
            f"Subjects Taught: {teacher.get('subjects', '')}\n"
            f"Research: {teacher.get('research', '')}\n"
            f"Achievements: {teacher.get('achievements', '')}\n"
            f"Free Periods: {teacher.get('free_periods', '')}\n"
        )

    # =========================================================
    # INDEX TEACHERS
    # =========================================================

    def index_teachers(self):

        if self.teacher_collection.count() > 0:

            print("Teachers already indexed")
            return

        for i, teacher in enumerate(self.teachers_data):

            teacher_id = f"teacher_{i}"

            chunk = self.teacher_to_text(
                teacher
            )

            self.teacher_collection.add(

                ids=[teacher_id],

                documents=[chunk],

                metadatas=[{
                    "name": teacher.get("name", ""),
                    "department": teacher.get(
                        "department",
                        ""
                    )
                }]
            )

        print(
            f"Indexed {len(self.teachers_data)} teachers"
        )

    # =========================================================
    # INDEX TIMETABLES
    # =========================================================


    def index_timetables(self):

                if self.timetable_collection.count() > 0:

                    print("Timetables already indexed")
                    return

                counter = 0

                teacher_schedule = {}

                for section, section_data in self.timetable_data.items():

                    department = section_data.get(
                        "department",
                        ""
                    )

                    incharge = section_data.get(
                        "class_incharge",
                        ""
                    )

                    strength = section_data.get(
                        "strength",
                        "Unknown"
                    )

                    timetable = section_data.get(
                        "timetable",
                        {}
                    )

                    # =====================================================
                    # SECTION MASTER CHUNK
                    # =====================================================

                    section_master = (
                        f"Department: {department}\n"
                        f"Section: {section}\n"
                        f"Class Incharge: {incharge}\n"
                        f"Strength: {strength}\n\n"
                    )

                    for day, periods in timetable.items():

                        section_master += f"{day}:\n"

                        # =============================================
                        # FULL DAY CHUNK
                        # =============================================

                        day_chunk = (
                            f"Department: {department}\n"
                            f"Section: {section}\n"
                            f"Class Incharge: {incharge}\n"
                            f"Strength: {strength}\n"
                            f"Day: {day}\n\n"
                        )

                        for period_num, info in periods.items():

                            subject = info.get(
                                "subject",
                                ""
                            )

                            teacher = info.get(
                                "teacher",
                                ""
                            )

                            room = info.get(
                                "room",
                                ""
                            )

                            # =========================================
                            # ADD TO SECTION MASTER
                            # =========================================

                            section_master += (
                                f"Period {period_num}: "
                                f"{subject} | "
                                f"{teacher}\n"
                            )

                            # =========================================
                            # EXACT PERIOD CHUNK
                            # =========================================

                            period_chunk = (
                                f"Department: {department}\n"
                                f"Section: {section}\n"
                                f"Class Incharge: {incharge}\n"
                                f"Strength: {strength}\n"
                                f"Day: {day}\n"
                                f"Period: {period_num}\n"
                                f"Subject: {subject}\n"
                                f"Teacher: {teacher}\n"
                                f"Room: {room}\n"
                            )

                            self.timetable_collection.add(

                                ids=[f"tt_{counter}"],

                                documents=[period_chunk],

                                metadatas=[{
                                    "type": "period",
                                    "section": section,
                                    "day": day,
                                    "period": str(period_num),
                                    "teacher": teacher,
                                    "subject": subject
                                }]
                            )

                            counter += 1

                            # =========================================
                            # DAY CHUNK CONTENT
                            # =========================================

                            day_chunk += (
                                f"Period {period_num}: "
                                f"{subject} | "
                                f"{teacher} | "
                                f"{room}\n"
                            )

                            # =========================================
                            # BUILD TEACHER MASTER SCHEDULE
                            # =========================================

                            if teacher:

                                if teacher not in teacher_schedule:

                                    teacher_schedule[teacher] = []

                                teacher_schedule[teacher].append(

                                    f"{day} Period {period_num} | "
                                    f"Section: {section} | "
                                    f"Subject: {subject} | "
                                    f"Room: {room}"
                                )

                        section_master += "\n"

                        # =============================================
                        # STORE DAY CHUNK
                        # =============================================

                        self.timetable_collection.add(

                            ids=[f"day_{section}_{day}"],

                            documents=[day_chunk],

                            metadatas=[{
                                "type": "day",
                                "section": section,
                                "day": day
                            }]
                        )

                    # =====================================================
                    # STORE SECTION MASTER CHUNK
                    # =====================================================

                    self.timetable_collection.add(

                        ids=[f"section_master_{section}"],

                        documents=[section_master],

                        metadatas=[{
                            "type": "section_master",
                            "section": section,
                            "class_incharge": incharge
                        }]
                    )

                # =====================================================
                # TEACHER MASTER CHUNKS
                # =====================================================

                for teacher, schedules in teacher_schedule.items():

                    master_chunk = (
                        f"Teacher: {teacher}\n\n"
                        f"Weekly Schedule:\n\n"
                        + "\n".join(schedules)
                    )

                    self.timetable_collection.add(

                        ids=[f"teacher_schedule_{teacher}"],

                        documents=[master_chunk],

                        metadatas=[{
                            "type": "teacher_schedule",
                            "teacher": teacher
                        }]
                    )

                print(
                    f"Indexed {counter} timetable entries"
                )
            

    def ask(self, question):

        question_lower = question.lower()

        # =====================================================
        # EXACT TIMETABLE QUERY
        # =====================================================

        section_match = re.search(
            r'(cse|ece|eee|mech)[\s-]?[abc]',
            question_lower
        )

        day_match = re.search(
            r'monday|tuesday|wednesday|thursday|friday',
            question_lower
        )

        period_match = re.search(
            r'(\d+)(st|nd|rd|th)?\s*period',
            question_lower
        )

        # =====================================================
        # EXACT FILTER SEARCH
        # =====================================================

        if (
            section_match and
            day_match and
            period_match
        ):

            section = (
                section_match.group(0)
                .upper()
                .replace(" ", "-")
            )

            if "-" not in section:
                section = (
                    section[:3]
                    + "-"
                    + section[3:]
                )

            day = (
                day_match.group(0)
                .capitalize()
            )

            period = (
                period_match.group(1)
            )

            timetable_results = (

                self.timetable_collection.query(

                    query_texts=[question],

                    n_results=3,

                    where={
                        "$and": [

                            {
                                "section": section
                            },

                            {
                                "day": day
                            },

                            {
                                "period": period
                            }
                        ]
                    }
                )
            )

        else:

            timetable_results = (

                self.timetable_collection.query(

                    query_texts=[question],

                    n_results=7
                )
            )

        # =====================================================
        # TEACHER SEARCH
        # =====================================================

        teacher_results = (

            self.teacher_collection.query(

                query_texts=[question],

                n_results=7
            )
        )

        # =====================================================
        # CONTEXT
        # =====================================================

        timetable_docs = (
            timetable_results["documents"][0]
        )

        teacher_docs = (
            teacher_results["documents"][0]
        )

        context = (
            "=== TIMETABLE DATA ===\n\n"
        )

        context += (
            "\n---\n".join(timetable_docs)
        )

        context += (
            "\n\n=== TEACHER DATA ===\n\n"
        )

        context += (
            "\n---\n".join(teacher_docs)
        )

        # =====================================================
        # PROMPT
        # =====================================================

        prompt = f"""
You are a college timetable assistant.

STRICT RULES:

1. Answer ONLY from context.
2. Never hallucinate.
3. If answer not found say:
"I could not find this information in the timetable data."
4. Give exact subject, teacher and room.
5. Be concise and accurate.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        response = (
            self.groq_client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[{
                    "role": "user",
                    "content": prompt
                }],

                temperature=0.0
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )

