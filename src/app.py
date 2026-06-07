import os
import shutil
from timetable_rag import TimetableRAG

STORAGE_PATH = "./storage/chroma_db"

def is_indexed(rag):
    """Properly check if data exists in ChromaDB collections"""
    try:
        teacher_count = rag.teacher_collection.count()
        timetable_count = rag.timetable_collection.count()
        print(f"Teachers in DB: {teacher_count}")
        print(f"Timetable entries in DB: {timetable_count}")
        return teacher_count > 0 and timetable_count > 0
    except Exception as e:
        print(f"Check failed: {e}")
        return False

def load_and_index(rag):
    """Load all data and index into ChromaDB"""
    print("\nLoading data files...")

    rag.load_timetable_json("../data/cse_timetable.json")
    rag.load_timetable_json("../data/ece_timetable.json")
    rag.load_timetable_json("../data/eee_timetable.json")
    rag.load_timetable_json("../data/mech_timetable.json")
    rag.extract_teachers_from_pdf("../data/teacher_biodata.pdf")

    print("\nIndexing teachers...")
    rag.index_teachers()

    print("\nIndexing timetables...")
    rag.index_timetables()

    print("\nIndexing complete!")

# ── Start ──────────────────────────────────────────────
rag = TimetableRAG()

if not is_indexed(rag):
    print("\nNo data found — indexing now...")
    load_and_index(rag)
else:
    print("Data already indexed — ready to use!")

print("\n" + "="*50)
print("AI Timetable Assistant Ready!")
print("="*50)
print("Commands: 'reindex' to refresh | 'exit' to quit\n")

while True:

    q = input("Ask Question: ").strip()

    if not q:
        continue

    if q.lower() == "exit":
        print("Goodbye!")
        break

    if q.lower() == "reindex":
        print("\nClearing old data...")
        # Delete ChromaDB storage completely
        shutil.rmtree(STORAGE_PATH, ignore_errors=True)
        os.makedirs(STORAGE_PATH, exist_ok=True)
        print("Storage cleared! Re-initializing...")
        # Re-create RAG with fresh ChromaDB
        rag = TimetableRAG()
        load_and_index(rag)
        print("\nReindex complete! You can ask questions now.\n")
        continue

    print("\nSearching...")
    ans = rag.ask(q)
    print("\nAnswer:")
    print(ans)
    print("-" * 50 + "\n")