# roblox_api.py
import requests
import config
import os

_csrf_token = ""

def refresh_csrf_token():
    global _csrf_token
    url = "https://auth.roblox.com/v1/logout"
    headers = {"Cookie": f".ROBLOSECURITY={config.ROBLOSECURITY}"}
    try:
        response = requests.post(url, headers=headers)
        if "X-CSRF-Token" in response.headers:
            _csrf_token = response.headers["X-CSRF-Token"]
        elif "x-csrf-token" in response.headers:
            _csrf_token = response.headers["x-csrf-token"]
    except Exception as e:
        print(f"Error refreshing token: {e}")

def get_session_headers():
    global _csrf_token
    if not _csrf_token:
        refresh_csrf_token()
    return {
        "Cookie": f".ROBLOSECURITY={config.ROBLOSECURITY}",
        "X-CSRF-Token": _csrf_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

def verify_cookie(cookie_value):
    config.ROBLOSECURITY = cookie_value.strip()
    refresh_csrf_token()
    url = "https://users.roblox.com/v1/users/authenticated"
    try:
        response = requests.get(url, headers=get_session_headers())
        if response.status_code == 200:
            data = response.json()
            config.USER_DATA["username"] = data.get("name", "")
            config.USER_DATA["user_id"] = str(data.get("id", ""))
            return True
        return False
    except:
        return False

def get_user_groups():
    if not config.USER_DATA["user_id"]: return []
    url = f"https://groups.roblox.com/v2/users/{config.USER_DATA['user_id']}/groups/roles"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return [{
                "id": str(item["group"]["id"]),
                "name": item["group"]["name"],
                "role": item["role"]["name"]
            } for item in response.json().get("data", [])]
        return []
    except:
        return []

def upload_audio(file_path, title, group_id=None):
    """رفع ملف صوتي (mp3 أو wav) إلى حسابك أو مجموعتك"""
    url = "https://publish.roblox.com/v1/audio"
    headers = get_session_headers()
    
    if not os.path.exists(file_path):
        return {"success": False, "error": "الملف الصوتي غير موجود محلياً"}
        
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "audio/mpeg")}
        data = {
            "name": title,
            "description": "Uploaded via Asset Manager",
            "creatorId": group_id if group_id else config.USER_DATA["user_id"],
            "creatorType": "Group" if group_id else "User"
        }
        try:
            response = requests.post(url, headers=headers, data=data, files=files)
            if response.status_code == 200:
                return {"success": True, "asset_id": response.json().get("assetId")}
            else:
                return {"success": False, "error": response.json().get("errors", [{}])[0].get("message", "فشل الرفع")}
        except Exception as e:
            return {"success": False, "error": str(e)}

def upload_animation(file_path, title, group_id=None):
    """رفع ملف أنميشن (FBX / أو صيغة روبلوكس المدعومة)"""
    url = "https://publish.roblox.com/v1/animations"
    headers = get_session_headers()
    
    if not os.path.exists(file_path):
        return {"success": False, "error": "ملف الأنميشن غير موجود"}

    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/octet-stream")}
        data = {
            "name": title,
            "description": "Animation Asset",
            "creatorId": group_id if group_id else config.USER_DATA["user_id"],
            "creatorType": "Group" if group_id else "User"
        }
        try:
            response = requests.post(url, headers=headers, data=data, files=files)
            if response.status_code == 200:
                return {"success": True, "asset_id": response.json().get("assetId")}
            else:
                return {"success": False, "error": response.json().get("errors", [{}])[0].get("message", "فشل الرفع")}
        except Exception as e:
            return {"success": False, "error": str(e)}
