from app.core.database import SessionLocal
from app.core.models import GSPRRequirement

def seed_gspr():
    db = SessionLocal()
    try:
        if db.query(GSPRRequirement).count() > 0:
            print("GSPR requirements already exist. Skipping.")
            return

        requirements = [
            {"chapter": "1", "section": "1", "full_reference": "GSPR 1", "text": "Devices shall achieve the performance intended by their manufacturer..."},
            {"chapter": "1", "section": "2", "full_reference": "GSPR 2", "text": "The requirement to reduce risks as far as possible..."},
            {"chapter": "1", "section": "3", "full_reference": "GSPR 3", "text": "Manufacturers shall establish, implement, document and maintain a risk management system..."},
            {"chapter": "2", "section": "10.1", "full_reference": "GSPR 10.1", "text": "Devices shall be designed and manufactured in such a way as to ensure that the characteristics and performance requirements referred to in Chapter I are fulfilled."},
            {"chapter": "2", "section": "11.1", "full_reference": "GSPR 11.1", "text": "Devices and their manufacturing processes shall be designed in such a way as to eliminate or to reduce as far as possible the risk of infection to patients..."}
        ]

        for req in requirements:
            db_req = GSPRRequirement(**req)
            db.add(db_req)
        
        db.commit()
        print(f"Seeded {len(requirements)} GSPR requirements.")

    except Exception as e:
        print(f"Error seeding GSPR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_gspr()
