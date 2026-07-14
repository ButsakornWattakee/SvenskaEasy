# -*- coding: utf-8 -*-
from pymongo import MongoClient
import os
import json
import sys

def get_mongo_uri():
    try:
        import streamlit as st
        if "MONGO_URI" in st.secrets:
            return st.secrets["MONGO_URI"]
    except Exception:
        pass
        
    env_uri = os.environ.get("MONGO_URI")
    # If the system has a generic localhost environment variable set, bypass it to use our Cloud Database
    if env_uri and "localhost" not in env_uri and "127.0.0.1" not in env_uri:
        return env_uri
        
    return "mongodb+srv://admin_easy:mypassword123@cluster0.e7pd0y4.mongodb.net/svenska_easy?retryWrites=true&w=majority"

MONGO_URI = get_mongo_uri()
DB_NAME = "svenska_easy"
COLLECTION_NAME = "users"
FALLBACK_FILE = "users_fallback.json"
DELETED_COLLECTION_NAME = "deleted_users"
DELETED_FALLBACK_FILE = "deleted_users_fallback.json"

_cached_client = None
_mongodb_online_status = None
_mongodb_last_checked = 0
CHECK_INTERVAL_SECONDS = 300  # Only re-verify connectivity status every 5 minutes

def is_mongodb_online_cached():
    global _mongodb_online_status, _mongodb_last_checked
    import time
    now = time.time()
    
    if _mongodb_online_status is not None and (now - _mongodb_last_checked) < CHECK_INTERVAL_SECONDS:
        return _mongodb_online_status
        
    client, err = get_db_client_direct()
    status = (client is not None)
    
    _mongodb_online_status = status
    _mongodb_last_checked = now
    return status

def get_db_client_direct():
    global _cached_client
    if _cached_client is not None:
        try:
            # Quick ping to verify cached connection is still active (only done during background status checks/reconnects)
            _cached_client.admin.command('ping')
            return _cached_client, None
        except Exception:
            _cached_client = None
            
    try:
        class SharedMongoClient(MongoClient):
            def close(self):
                # No-op to preserve connection pooling across Streamlit reruns
                pass
                
        client = SharedMongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        _cached_client = client
        return client, None
    except Exception as e:
        print(f"⚠️ SharedMongoClient Connection Failed: {e}", file=sys.stderr)
        return None, str(e)

def get_db_client():
    global _cached_client
    # Return cached client immediately without pinging to eliminate query latency
    if _cached_client is not None:
        return _cached_client, None
        
    return get_db_client_direct()

def is_mongodb_online():
    return is_mongodb_online_cached()

# --- FALLBACK JSON DB METHODS ---
def load_fallback_deleted_users():
    if not os.path.exists(DELETED_FALLBACK_FILE):
        return {}
    try:
        with open(DELETED_FALLBACK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_fallback_deleted_users(deleted_dict):
    try:
        with open(DELETED_FALLBACK_FILE, 'w', encoding='utf-8') as f:
            json.dump(deleted_dict, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"❌ Error saving fallback deleted users: {str(e)}", file=sys.stderr)
        return False

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
                "role": "Admin",
                "completed_lessons": [],
                "quiz_scores": {}
            })
            print("🌱 Default admin user seeded in MongoDB.")
        else:
            if "role" not in admin_user:
                users_col.update_one({"username": "admin"}, {"$set": {"role": "Admin"}})
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
        if user:
            if "role" not in user:
                user["role"] = "Admin" if user["username"] == "admin" else "User"
            if "avatar" in user and user["avatar"]:
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
        if user:
            if "role" not in user:
                user["role"] = "Admin" if user["username"] == "admin" else "User"
        return user
    except Exception as e:
        print(f"❌ Error getting user {username} from MongoDB: {str(e)}", file=sys.stderr)
        return None
    finally:
        client.close()

def create_user(username, email, password, role="User"):
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
            "role": role,
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
            "role": role,
            "completed_lessons": [],
            "quiz_scores": {}
        })
        return True, "สมัครสมาชิกสำเร็จ"
    except Exception as e:
        print(f"❌ Error creating user {username} in MongoDB: {str(e)}", file=sys.stderr)
        return False, f"เกิดข้อผิดพลาด MongoDB: {str(e)}"
    finally:
        client.close()

def update_last_active(username):
    client, err = get_db_client()
    from datetime import datetime
    now_str = datetime.utcnow().isoformat()
    
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        username_clean = username.strip()
        if username_clean in users:
            users[username_clean]["last_active"] = now_str
            save_fallback_users(users)
        return
        
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        users_col.update_one({"username": username.strip()}, {"$set": {"last_active": now_str}})
    except Exception as e:
        print(f"❌ Error updating last active for {username}: {str(e)}", file=sys.stderr)
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
            if "role" not in u_copy:
                u_copy["role"] = "Admin" if u_copy["username"] == "admin" else "User"
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
        for u in users_list:
            if "role" not in u:
                u["role"] = "Admin" if u["username"] == "admin" else "User"
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

def delete_user(username):
    from datetime import datetime
    deleted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client, err = get_db_client()
    
    if client is None:
        # Fallback to JSON database
        users = load_fallback_users()
        username_clean = username.strip()
        if username_clean in users:
            user_data = users[username_clean]
            user_data["deleted_at"] = deleted_time
            
            # Save to deleted fallback JSON
            deleted_users = load_fallback_deleted_users()
            deleted_users[username_clean] = user_data
            if save_fallback_deleted_users(deleted_users):
                del users[username_clean]
                return save_fallback_users(users)
        return False
        
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        deleted_col = db[DELETED_COLLECTION_NAME]
        
        user_data = users_col.find_one({"username": username.strip()})
        if user_data:
            user_data["deleted_at"] = deleted_time
            # Keep avatar as binary if it exists
            # Delete any existing document in deleted_col with this username first to avoid _id conflict
            deleted_col.delete_many({"username": username.strip()})
            # Insert to deleted_users collection
            deleted_col.insert_one(user_data)
            # Remove from users collection
            result = users_col.delete_one({"username": username.strip()})
            return result.deleted_count > 0
        return False
    except Exception as e:
        print(f"❌ Error deleting user {username} from MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()

def get_deleted_users():
    client, err = get_db_client()
    if client is None:
        # Fallback to JSON database
        deleted_users = load_fallback_deleted_users()
        users_list = []
        import base64
        for u in deleted_users.values():
            u_copy = dict(u)
            if "role" not in u_copy:
                u_copy["role"] = "Admin" if u_copy["username"] == "admin" else "User"
            if u_copy.get("avatar"):
                try:
                    u_copy["avatar"] = base64.b64decode(u_copy["avatar"])
                except Exception:
                    pass
            users_list.append(u_copy)
        return users_list
        
    try:
        db = client[DB_NAME]
        deleted_col = db[DELETED_COLLECTION_NAME]
        deleted_list = list(deleted_col.find({}))
        for u in deleted_list:
            if "role" not in u:
                u["role"] = "Admin" if u["username"] == "admin" else "User"
        return deleted_list
    except Exception as e:
        print(f"❌ Error getting deleted users from MongoDB: {str(e)}", file=sys.stderr)
        return []
    finally:
        client.close()

def restore_user(username):
    client, err = get_db_client()
    if client is None:
        # Fallback to JSON database
        deleted_users = load_fallback_deleted_users()
        username_clean = username.strip()
        if username_clean in deleted_users:
            user_data = deleted_users[username_clean]
            user_data.pop("deleted_at", None)
            
            users = load_fallback_users()
            users[username_clean] = user_data
            if save_fallback_users(users):
                del deleted_users[username_clean]
                save_fallback_deleted_users(deleted_users)
                return True
        return False
        
    try:
        db = client[DB_NAME]
        users_col = db[COLLECTION_NAME]
        deleted_col = db[DELETED_COLLECTION_NAME]
        
        user_data = deleted_col.find_one({"username": username.strip()})
        if user_data:
            user_data.pop("deleted_at", None)
            # Delete any existing document in users_col with this username first to avoid _id conflict
            users_col.delete_many({"username": username.strip()})
            # Restore to users collection
            users_col.insert_one(user_data)
            # Remove from deleted collection
            deleted_col.delete_one({"username": username.strip()})
            return True
        return False
    except Exception as e:
        print(f"❌ Error restoring user {username} in MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()

def delete_user_permanently(username):
    client, err = get_db_client()
    if client is None:
        # Fallback to JSON database
        deleted_users = load_fallback_deleted_users()
        username_clean = username.strip()
        if username_clean in deleted_users:
            del deleted_users[username_clean]
            return save_fallback_deleted_users(deleted_users)
        return False
        
    try:
        db = client[DB_NAME]
        deleted_col = db[DELETED_COLLECTION_NAME]
        result = deleted_col.delete_one({"username": username.strip()})
        return result.deleted_count > 0
    except Exception as e:
        print(f"❌ Error permanently deleting user {username} from MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()



GAME_IMAGES_COLLECTION_NAME = "game_images"
FALLBACK_GAME_IMAGES_PATH = "fallback_game_images.json"

def load_fallback_game_images():
    import json
    if not os.path.exists(FALLBACK_GAME_IMAGES_PATH):
        return {}
    try:
        with open(FALLBACK_GAME_IMAGES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_fallback_game_images(images):
    import json
    try:
        with open(FALLBACK_GAME_IMAGES_PATH, "w", encoding="utf-8") as f:
            json.dump(images, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def save_game_image(swedish_word, image_bytes):
    word_key = swedish_word.strip().lower()
    client, err = get_db_client()
    
    import base64
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    if client is None:
        images = load_fallback_game_images()
        images[word_key] = {
            "swedish": word_key,
            "image_data": encoded_image
        }
        return save_fallback_game_images(images)
        
    try:
        db = client[DB_NAME]
        col = db[GAME_IMAGES_COLLECTION_NAME]
        col.replace_one(
            {"swedish": word_key},
            {"swedish": word_key, "image_data": encoded_image},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"❌ Error saving game image for {swedish_word} in MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()

def get_game_image(swedish_word):
    word_key = swedish_word.strip().lower()
    client, err = get_db_client()
    
    import base64
    if client is None:
        images = load_fallback_game_images()
        item = images.get(word_key)
        if item and "image_data" in item:
            try:
                return base64.b64decode(item["image_data"])
            except Exception:
                pass
        return None
        
    try:
        db = client[DB_NAME]
        col = db[GAME_IMAGES_COLLECTION_NAME]
        doc = col.find_one({"swedish": word_key})
        if doc and "image_data" in doc:
            try:
                return base64.b64decode(doc["image_data"])
            except Exception:
                pass
        return None
    except Exception as e:
        print(f"❌ Error getting game image for {swedish_word} from MongoDB: {str(e)}", file=sys.stderr)
        return None
    finally:
        client.close()

def get_all_game_images():
    client, err = get_db_client()
    if client is None:
        images = load_fallback_game_images()
        return list(images.keys())
        
    try:
        db = client[DB_NAME]
        col = db[GAME_IMAGES_COLLECTION_NAME]
        docs = col.find({}, {"swedish": 1})
        return [doc["swedish"] for doc in docs]
    except Exception as e:
        print(f"❌ Error getting game images list from MongoDB: {str(e)}", file=sys.stderr)
        return []
    finally:
        client.close()

def delete_game_image(swedish_word):
    word_key = swedish_word.strip().lower()
    client, err = get_db_client()
    if client is None:
        images = load_fallback_game_images()
        if word_key in images:
            del images[word_key]
            return save_fallback_game_images(images)
        return False
        
    try:
        db = client[DB_NAME]
        col = db[GAME_IMAGES_COLLECTION_NAME]
        res = col.delete_one({"swedish": word_key})
        return res.deleted_count > 0
    except Exception as e:
        print(f"❌ Error deleting game image for {swedish_word} in MongoDB: {str(e)}", file=sys.stderr)
        return False
    finally:
        client.close()


