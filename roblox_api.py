import requests
import os
import config

def upload_audio(file_path, title, group_id=None):
    """
    دالة مطورة لرفع الملفات الصوتية (WAV / MP3) إلى روبلوكس مع صياغة Multipart صحيحة
    """
    # 1. التحقق من وجود الملف محلياً
    if not os.path.exists(file_path):
        return {"success": False, "error": "الملف غير موجود في المسار المحدد!"}
    
    # 2. تحديد عنوان الـ API المناسب للرفع (قد يتطلب الرفع الحديث استخدام الـ Open Cloud API أو Publish API)
    url = "https://publish.roblox.com/v1/assets/upload" # أو الرابط المعتمد في السكربت الخاص بك
    
    # 3. تجهيز الـ Headers والـ الكوكيز والـ CSRF Token
    # تأكد من جلب الـ X-CSRF-TOKEN أولاً إذا كان السيرفر يتطلبه
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        # "X-CSRF-TOKEN": roblox_api.get_csrf_token() # إذا كنت تستخدم دالة لجلب التوكن
    }
    
    cookies = {
        ".ROBLOSECURITY": config.USER_DATA.get("cookie", "")
    }
    
    # 4. تجهيز البيانات النصية المرافقة (Metadata)
    data = {
        "assetType": "Audio",
        "displayName": title,
        "description": "Uploaded via Asset Manager",
    }
    if group_id:
        data["groupId"] = str(group_id)
        
    # 5. التغليف الصحيح للملف (هنا تكمن حل المشكلة الظاهرة في الصورة)
    file_name = os.path.basename(file_path)
    # نحدد نوع الـ Content-Type بناءً على الامتداد لكي يقبله السيرفر فوراً
    content_type = "audio/wav" if file_name.lower().endswith('.wav') else "audio/mpeg"
    
    try:
        with open(file_path, 'rb') as f:
            # إرسال الملف باسم الحقل البرمجي المتوقع (غالباً 'file' أو 'request')
            files = {
                'file': (file_name, f, content_type)
            }
            
            response = requests.post(url, headers=headers, cookies=cookies, data=data, files=files)
            
            # فحص استجابة السيرفر
            if response.status_code == 200:
                res_json = response.json()
                return {"success": True, "asset_id": res_json.get("assetId")}
            else:
                # محاولة قراءة الخطأ القادم من السيرفر بشكل مفصل
                try:
                    err_msg = response.json().get("errors", [{}])[0].get("message", response.text)
                except:
                    err_msg = response.text
                return {"success": False, "error": f"كود الخطأ: {response.status_code} - {err_msg}"}
                
    except Exception as e:
        return {"success": False, "error": str(e)}
