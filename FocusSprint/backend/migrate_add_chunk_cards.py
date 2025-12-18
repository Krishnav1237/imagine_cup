import os
import sqlite3
import argparse
import subprocess
from pathlib import Path

from app.config import settings

def resolve_db_path(provided_db: str = None) -> Path:
    # Prefer explicit CLI arg
    if provided_db:
        return Path(provided_db)

    # Prefer settings DB URL if it's SQLite
    db_url = getattr(settings, "DATABASE_URL", None) or getattr(settings, "SQLALCHEMY_DATABASE_URI", None)
    if db_url and db_url.startswith("sqlite:///"):
        return Path(db_url.replace("sqlite:///", ""))

    # Fallback common path used in this project
    possible = Path("./data/adhd_learning.db")
    if possible.exists():
        return possible

    # last resort: local app.db
    return Path("app.db")

def apply_alters(db_path: Path):
    if not db_path.exists():
        raise SystemExit(f"DB file not found: {db_path.resolve()}")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(content_chunks);")
    existing_cols = [r[1] for r in cur.fetchall()]

    stmts = []
    if "card_json" not in existing_cols:
        stmts.append("ALTER TABLE content_chunks ADD COLUMN card_json TEXT")
    if "source_file" not in existing_cols:
        stmts.append("ALTER TABLE content_chunks ADD COLUMN source_file VARCHAR(512)")
    if "source_page" not in existing_cols:
        stmts.append("ALTER TABLE content_chunks ADD COLUMN source_page INTEGER")
    if "source_slide" not in existing_cols:
        stmts.append("ALTER TABLE content_chunks ADD COLUMN source_slide INTEGER")

    if not stmts:
        print("No changes needed — all columns already exist.")
    else:
        for s in stmts:
            try:
                cur.execute(s)
                print("OK:", s)
            except Exception as e:
                print("Failed:", s, "->", e)
        conn.commit()

    # show final schema for verification
    cur.execute("PRAGMA table_info(content_chunks);")
    print("content_chunks columns:", [r[1] for r in cur.fetchall()])
    conn.close()

def alembic_stamp(db_path: Path, revision: str = "add_chunk_card_columns"):
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    try:
        subprocess.run(["alembic", "stamp", revision], check=True, env=env)
        print(f"Alembic stamped revision {revision}")
    except Exception as e:
        print("Alembic stamp failed:", e)

def main():
    ap = argparse.ArgumentParser(description="Apply schema changes to add chunk-card columns.")
    ap.add_argument("--db", help="Path to sqlite DB file (overrides settings)", default=None)
    ap.add_argument("--stamp", action="store_true", help="Run `alembic stamp add_chunk_card_columns` after applying changes")
    args = ap.parse_args()

    db_path = resolve_db_path(args.db)
    print("Using DB path:", db_path.resolve())
    apply_alters(db_path)
    if args.stamp:
        alembic_stamp(db_path)

if __name__ == "__main__":
    main()