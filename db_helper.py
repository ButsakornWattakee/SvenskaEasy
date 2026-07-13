# -*- coding: utf-8 -*-
from pymongo import MongoClient
import os
import json
import sys

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "svenska_easy"
COLLECTION_NAME = "users"
FALLBACK_FILE = "users_fallback.json"

def is_mongodb_online():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        client.admin.command('ping')
        client.close()
        return True
    except Exception:
        return False

def get_db_client():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
        client.admin.command('ping')
        return client, None
    except Exception as e:
        return None, str(e)

# --- FALLBACK JSON DB METHODS ---
def load_fallback_users():
    if not os.path.exists(FALLBACK_FILE):
        default_users = {
            "admin": {
                "username": "admin",
                "email": "admin@svenskaeasy.com",
                "password": "admin",
                "completed_lessons": [],
                "quiz_scores": {}
            }
        }
        save_fallback_users(default_users)
        return default_users
    try:
        with open(FALLBACK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_fallback_users(users_dict):
    try:
        with open(FALLBACK_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_dict, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"❌ Error saving fallback users: {str(e)}", file=sys.stderr)
        return False

# --- MAIN DATABASE INTERFACES ---
def init_db():
    client, err = get_db_client()
    if client is None:
        # Initialize JSON fallback database
        load_fallback_users()
        print("⚠️ MongoDB offline. Initialized local JSON fallback.")
        return True
    
    try:
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
            users_col.insert_one({
                "username": "admin",
                "email": "admin@svenskaeasy.com",
                "password": "admin",
                "completed_lessons": [],
                "quiz_scores": {}
            })
            print("🌱 Default admin user seeded in MongoDB.")
    except Exception as e:
        print(f"❌ Error during MongoDB initialization: {str(e)}", file=sys.stderr)
    finally:
        client.close()
    return True

def get_user(username):
    client, err = get_db_client()
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        user = users.get(username.strip())
        if user and "avatar" in user and user["avatar"]:
            import base64
            try:
                user["avatar"] = base64.b64decode(user["avatar"])
            except Exception:
                pass
        return user
        
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        user = users_col.find_one({"username": username.strip()})
        return user
    except Exception as e:
        print(f"❌ Error getting user {username} from MongoDB: {str(e)}", file=sys.stderr)
        return None
    finally:
        client.close()

def create_user(username, email, password):
    client, err = get_db_client()
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        username_clean = username.strip()
        email_clean = email.strip().lower()
        
        # Check if username or email exists in fallback
        if username_clean in users:
            return False, f"ชื่อผู้ใช้ '{username_clean}' ถูกใช้งานไปแล้ว"
            
        for u in users.values():
            if u.get("email") == email_clean:
                return False, f"อีเมล '{email_clean}' ถูกใช้งานไปแล้ว"
                
        users[username_clean] = {
            "username": username_clean,
            "email": email_clean,
            "password": password,
            "completed_lessons": [],
            "quiz_scores": {}
        }
        
        if save_fallback_users(users):
            return True, "สมัครสมาชิกสำเร็จ (บันทึกข้อมูลในโหมดจำลองชั่วคราว)"
        else:
            return False, "เกิดข้อผิดพลาดในการบันทึกข้อมูลโหมดจำลอง"
            
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        
        # Check if username or email already exists in MongoDB
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
        print(f"❌ Error creating user {username} in MongoDB: {str(e)}", file=sys.stderr)
        return False, f"เกิดข้อผิดพลาด MongoDB: {str(e)}"
    finally:
        client.close()

def update_user_progress(username, completed_lessons):
    client, err = get_db_client()
    lessons_list = list(completed_lessons)
    
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        username_clean = username.strip()
        if username_clean in users:
            users[username_clean]["completed_lessons"] = lessons_list
            return save_fallback_users(users)
        return False
        
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        users_col.update_one(
            {"username": username.strip()},
            {"$set": {"completed_lessons": lessons_list}}
        )
        return True
    except Exception as e:
        print(f"❌ Error updating progress for {username} in MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()

def update_user_quiz_scores(username, quiz_scores):
    client, err = get_db_client()
    
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        username_clean = username.strip()
        if username_clean in users:
            users[username_clean]["quiz_scores"] = quiz_scores
            return save_fallback_users(users)
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
        print(f"❌ Error updating quiz scores for {username} in MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()

def get_all_users():
    client, err = get_db_client()
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        # Decode base64 avatar for all users
        users_list = []
        import base64
        for u in users.values():
            u_copy = dict(u)
            if u_copy.get("avatar"):
                try:
                    u_copy["avatar"] = base64.b64decode(u_copy["avatar"])
                except Exception:
                    pass
            users_list.append(u_copy)
        return users_list
        
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        users_list = list(users_col.find({}))
        return users_list
    except Exception as e:
        print(f"❌ Error getting all users from MongoDB: {str(e)}", file=sys.stderr)
        return []
    finally:
        client.close()

def update_user_profile(username, phone, avatar_bytes):
    client, err = get_db_client()
    
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        username_clean = username.strip()
        if username_clean in users:
            users[username_clean]["phone"] = phone
            if avatar_bytes:
                import base64
                users[username_clean]["avatar"] = base64.b64encode(avatar_bytes).decode('utf-8')
            else:
                users[username_clean]["avatar"] = None
            return save_fallback_users(users)
        return False
        
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        
        update_data = {"phone": phone}
        if avatar_bytes:
            update_data["avatar"] = avatar_bytes
            
        users_col.update_one(
            {"username": username.strip()},
            {"$set": update_data}
        )
        return True
    except Exception as e:
        print(f"❌ Error updating profile for {username} in MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()

