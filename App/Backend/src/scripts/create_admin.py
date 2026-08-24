import os

from dotenv import load_dotenv

from Backend.database import SessionLocal
from Backend.src.core.security import hash_password
from Backend.src.models.user import User
from Backend.src.services.auth_service import generate_uid

load_dotenv()


def create_admin():
    db = SessionLocal()

    try:
        existing_admin = (
            db.query(User)
            .filter(User.role == "admin")
            .first()
        )

        if existing_admin:
            print("Admin already exists")
            return

        uid = generate_uid(db)

        admin = User(
            uid=uid,
            username="lmsadmin",
            email=os.getenv("ADMIN_EMAIL"),
            recovery_email=None,
            password_hash=hash_password(os.getenv("ADMIN_PASSWORD")),
            role="admin",
            email_verified=True,
            recovery_email_verified=False,
            is_active=True,
            deactivated_at=None
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully")
        print("Email:", os.getenv("ADMIN_EMAIL"))

    except Exception as e:
        db.rollback()
        print("Error creating admin:", e)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()