# main.py
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import config
import roblox_api
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Asset Manager - تسجيل الدخول")
        self.geometry("450x250")
        self.resizable(False, False)
        
        # تشغيل واجهة تسجيل الدخول
        self.setup_login_ui()

    def setup_login_ui(self):
        self.clear_window()
        
        tk.Label(self, text="🔑 سجل دخولك باستخدام كوكيز روبلوكس", font=("Arial", 11, "bold")).pack(pady=15)
        
        tk.Label(self, text="أدخل كوكيز .ROBLOSECURITY:").pack(pady=2)
        self.txt_cookie = tk.Entry(self, width=50, show="*")
        self.txt_cookie.pack(pady=5)
        
        self.btn_login = tk.Button(self, text="🔗 التحقق وربط الحساب", command=self.login, bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), width=20)
        self.btn_login.pack(pady=15)
        
        self.lbl_status = tk.Label(self, text="الحالة: غير متصل", fg="red")
        self.lbl_status.pack(pady=5)

    def login(self):
        cookie = self.txt_cookie.get().strip()
        if not cookie:
            messagebox.showwarning("تنبيه", "الرجاء إدخال الكوكيز أولاً!")
            return
        
        self.btn_login.config(text="جاري التحقق...", state="disabled")
        self.update()
        
        if roblox_api.verify_cookie(cookie):
            messagebox.showinfo("نجاح", f"أهلاً {config.USER_DATA['username']}! تم ربط الحساب بنجاح.")
            # الانتقال الفوري للوحة التحكم
            self.setup_main_dashboard_ui()
        else:
            messagebox.showerror("خطأ", "الكوكيز غير صحيح أو منتهي الصلاحية!")
            self.btn_login.config(text="🔗 التحقق وربط الحساب", state="normal")

    def setup_main_dashboard_ui(self):
        """بناء لوحة التحكم الكاملة للرفع بعد إصلاح الخطأ"""
        self.clear_window()
        self.title(f"Roblox Asset Manager - لوحة التحكم ({config.USER_DATA['username']})")
        self.geometry("550x500")
        self.resizable(False, False)
        
        # شريط معلومات المستخدم العلوي (تم إصلاح العرض هنا)
        user_frame = tk.Frame(self, bg="#34495e")
        user_frame.pack(fill="x", pady=(0, 15))
        
        lbl_welcome = tk.Label(user_frame, text=f"👤 المستخدم: {config.USER_DATA['username']} | ID: {config.USER_DATA['user_id']}", fg="white", bg="#34495e", font=("Arial", 10, "bold"))
        lbl_welcome.pack(pady=10, padx=10, side="left")
        
        # جلب المجموعات من ملف الـ API
        self.groups = roblox_api.get_user_groups()
        
        # 1. اختيار جهة الرفع
        tk.Label(self, text="🎯 اختر مكان الرفع (حسابك أو مجموعتك):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=5)
        
        self.upload_target_combo = ttk.Combobox(self, state="readonly")
        combo_values = ["حسابي الشخصي (My Profile)"]
        for g in self.groups:
            combo_values.append(f"مجموعة: {g['name']} (ID: {g['id']}) - رتبتك: {g['role']}")
        
        self.upload_target_combo['values'] = combo_values
        self.upload_target_combo.current(0)
        self.upload_target_combo.pack(pady=5, padx=20, fill="x")
        
        # 2. حقل إدخال اسم الـ Asset
        tk.Label(self, text="📝 اسم الملف في روبلوكس (Title):", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=5)
        self.txt_title = tk.Entry(self)
        self.txt_title.pack(pady=5, padx=20, fill="x")
        
        # 3. قسم اختيار الملف من الجهاز
        tk.Label(self, text="📁 اختر الملف من جهازك:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=5)
        
        file_frame = tk.Frame(self)
        file_frame.pack(pady=5, padx=20, fill="x")
        
        self.txt_file_path = tk.Entry(file_frame)
        self.txt_file_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_browse = tk.Button(file_frame, text="استعراض...", command=self.browse_file)
        btn_browse.pack(side="right")
        
        # 4. نوع الرفع (صوت أو أنميشن)
        tk.Label(self, text="⚙️ نوع الملف المراد رفعه:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=5)
        self.asset_type = tk.StringVar(value="audio")
        
        radio_frame = tk.Frame(self)
        radio_frame.pack(pady=5)
        tk.Radiobutton(radio_frame, text="ملف صوتي (MP3 / WAV)", variable=self.asset_type, value="audio").pack(side="left", padx=20)
        tk.Radiobutton(radio_frame, text="أنميشن (FBX / Animation)", variable=self.asset_type, value="animation").pack(side="left", padx=20)
        
        # 5. زر الرفع النهائي
        self.btn_upload = tk.Button(self, text="🚀 بدء الرفع إلى روبلوكس", command=self.start_upload, bg="#e67e22", fg="white", font=("Arial", 12, "bold"))
        self.btn_upload.pack(pady=25, padx=20, fill="x")

    def browse_file(self):
        file_types = [("All Supported Files", "*.mp3 *.wav *.fbx"), ("Audio Files", "*.mp3 *.wav"), ("Animation Files", "*.fbx")]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        if selected_file:
            self.txt_file_path.delete(0, tk.END)
            self.txt_file_path.insert(0, selected_file)
            
            base_name = os.path.splitext(os.path.basename(selected_file))[0]
            self.txt_title.delete(0, tk.END)
            self.txt_title.insert(0, base_name)

    def start_upload(self):
        file_path = self.txt_file_path.get().strip()
        title = self.txt_title.get().strip()
        
        if not file_path or not title:
            messagebox.showwarning("تنبيه", "الرجاء تحديد الملف وكتابة الاسم أولاً!")
            return
            
        selected_index = self.upload_target_combo.current()
        group_id = None
        if selected_index > 0:
            group_id = self.groups[selected_index - 1]["id"]
            
        self.btn_upload.config(text="جاري الرفع الآن... انتظر قليلاً", state="disabled")
        self.update()
        
        if self.asset_type.get() == "audio":
            result = roblox_api.upload_audio(file_path, title, group_id)
        else:
            result = roblox_api.upload_animation(file_path, title, group_id)
            
        if result.get("success"):
            messagebox.showinfo("تم الرفع بنجاح! 🎉", f"تم رفع الملف بنجاح!\nAsset ID: {result.get('asset_id')}")
            self.clipboard_clear()
            self.clipboard_append(str(result.get('asset_id')))
        else:
            messagebox.showerror("فشل الرفع ❌", f"حدث خطأ أثناء الرفع:\n{result.get('error')}")
            
        self.btn_upload.config(text="🚀 بدء الرفع إلى روبلوكس", state="normal")

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
