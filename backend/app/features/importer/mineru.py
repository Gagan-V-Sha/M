import csv
import json
import argparse
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, create_tables
from app.core.models import Standard, EvidenceDocument

# helper function to clean up text and handle empty values
def normalize_text(text):
    if not text:
        return None
    stripped = text.strip()
    return stripped if stripped else None

# function to load technical standards from a CSV file into the database
def import_standards(db: Session, file_path: str):
    print(f"Importing standards from {file_path}...")
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                code = normalize_text(row.get('code'))
                if not code:
                    continue

                # skip if this standard is already in our database
                existing = db.query(Standard).filter(Standard.code == code).first()
                if existing:
                    print(f"Skipping duplicate standard: {code}")
                    continue

                # handle the publication date format
                pub_date_str = normalize_text(row.get('publication_date'))
                pub_date = None
                if pub_date_str:
                    try:
                        pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d')
                    except ValueError:
                        print(f"Warning: Invalid date format for {code}: {pub_date_str}")

                # save the new standard
                standard = Standard(
                    code=code,
                    title=normalize_text(row.get('title')),
                    version=normalize_text(row.get('version')),
                    harmonised=row.get('harmonised', 'False').lower() == 'true',
                    oj_reference=normalize_text(row.get('oj_reference')),
                    status=normalize_text(row.get('status')),
                    publication_date=pub_date
                )
                db.add(standard)
                count += 1
            
            db.commit()
            print(f"Successfully imported {count} standards.")
    except Exception as e:
        print(f"Error importing standards: {e}")
        db.rollback()

# function to load evidence document info (like test reports) from a CSV
def import_evidence(db: Session, file_path: str):
    print(f"Importing evidence documents from {file_path}...")
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                tdd_number = normalize_text(row.get('tdd_number'))
                if not tdd_number:
                    continue

                # skip if this document number already exists
                existing = db.query(EvidenceDocument).filter(EvidenceDocument.tdd_number == tdd_number).first()
                if existing:
                    print(f"Skipping duplicate evidence: {tdd_number}")
                    continue

                evidence = EvidenceDocument(
                    tdd_number=tdd_number,
                    title=normalize_text(row.get('title')),
                    version=normalize_text(row.get('version')),
                    type=normalize_text(row.get('type')),
                    owner=normalize_text(row.get('owner')),
                    path=normalize_text(row.get('path'))
                )
                db.add(evidence)
                count += 1
            
            db.commit()
            print(f"Successfully imported {count} evidence documents.")
    except Exception as e:
        print(f"Error importing evidence: {e}")
        db.rollback()

# main part of the script that handles command line arguments
def main():
    parser = argparse.ArgumentParser(description="Import data into GSPR database.")
    parser.add_argument('--standards', help="Path to standards CSV file")
    parser.add_argument('--evidence', help="Path to evidence CSV file")

    args = parser.parse_args()

    # ensure the database exists
    create_tables()

    db = SessionLocal()
    try:
        if args.standards:
            import_standards(db, args.standards)
        
        if args.evidence:
            import_evidence(db, args.evidence)
        
        if not args.standards and not args.evidence:
            print("No files provided. Use --standards or --evidence.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
