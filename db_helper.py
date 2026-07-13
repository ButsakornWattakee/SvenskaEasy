# -*- coding: utf-8 -*-
from pymongo import MongoClient
import sys

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "svenska_easy"
COLLECTION_NAME = "users"

def get_db_client():
    try:
        # Set a short server selection timeout so it fails quickly if MongoDB is not running
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        # Test connection by pinging
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB at {MONGO_URI}: {str(e)}", file=sys.stderr)
        return None

def init_db():
    client = get_db_client()
    if client is None:
        return False
    
    db = client[DB_NAME]
    users_col = db[COLLECTION_NAME]
    
    # Ensure unique index on username
    try:
        users_col.create_index("username", unique=True)
    except Exception:
        pass
        
    # Seed default admin user if not present
    admin_user = users_col.find_one({"username": "admin"})
    if not admin_user:
        try:
            users_col.insert_one({
                "username": "admin",
                "email": "admin@svenskaeasy.com",
                "password": "admin",
                "completed_lessons": [],
                "quiz_scores": {}
            })
            print("🌱 Default admin user seeded successfully.")
        except Exception as e:
            print(f"❌ Error seeding admin user: {str(e)}", file=sys.stderr)
            
    client.close()
    return True

def get_user(username):
    client = get_db_client()
    if client is None:
        return None
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        user = users_col.find_one({"username": username.strip()})
        return user
    except Exception as e:
        print(f"❌ Error getting user {username}: {str(e)}", file=sys.stderr)
        return None
    finally:
        client.close()

def create_user(username, email, password):
    client = get_db_client()
    if client is None:
        return False, "ไม่สามารถเชื่อมต่อฐานข้อมูลได้"
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        
        # Check if username or email already exists
        if users_col.find_one({"username": username.strip()}):
            return False, f"ชื่อผู้ใช้ '{username}' ถูกใช้งานไปแล้ว"
            
        if users_col.find_one({"email": email.strip().lower()}):
            return False, f"อีเมล '{email}' ถูกใช้งานไปแล้ว"
            
        users_col.insert_one({
            "username": username.strip(),
            "email": email.strip().lower(),
            "password": password,
            "completed_lessons": [],
            "quiz_scores": {}
        })
        return True, "สมัครสมาชิกสำเร็จ"
    except Exception as e:
        print(f"❌ Error creating user {username}: {str(e)}", file=sys.stderr)
        return False, f"เกิดข้อผิดพลาด: {str(e)}"
    finally:
        client.close()

def update_user_progress(username, completed_lessons):
    client = get_db_client()
    if client is None:
        return False
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        # completed_lessons is a set in session_state, convert to list for mongodb
        lessons_list = list(completed_lessons)
        users_col.update_one(
            {"username": username.strip()},
            {"$set": {"completed_lessons": lessons_list}}
        )
        return True
    except Exception as e:
        print(f"❌ Error updating progress for {username}: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()

def update_user_quiz_scores(username, quiz_scores):
    client = get_db_client()
    if client is None:
        return False
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        users_col.update_one(
            {"username": username.strip()},
            {"$set": {"quiz_scores": quiz_scores}}
        )
        return True
    except Exception as e:
        print(f"❌ Error updating quiz scores for {username}: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()
