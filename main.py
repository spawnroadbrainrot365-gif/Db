# main.py
import tkinter as tk
from tkinter import messagebox
import config
import roblox_api

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Asset Manager")
        self.geometry("450x300")
        
        tk.Label(self, text="أدخل كوكيز .ROBLOSECURITY:").pack(pady=10)
        self.txt_cookie = tk.Entry(self, width=50)
        self.txt_cookie.pack(pady=5)
        
        tk.Button(self, text="التحقق وربط الحساب", command=self.login).pack(pady=15)
        self.lbl_status = tk.Label(self, text="الحالة: غير متصل", fg="red")
        self.lbl_status.pack(pady=5)

    def login(self):
        cookie = self.txt_cookie.get().strip()
        if not cookie: return
        
        if roblox_api.verify_cookie(cookie):
            groups = roblox_api.get_user_groups()
            status_text = f"متصل: {config.USER_DATA['username']}\nعدد المجموعات المكتشفة: {len(groups)}"
            self.lbl_status.config(text=status_text, fg="green")
            messagebox.showinfo("نجاح", f"أهلاً {config.USER_DATA['username']}! تم تحميل بياناتك ومجموعاتك بنجاح.")
        else:
            messagebox.showerror("خطأ", "الكوكيز غير صحيح أو منتهي الصلاحية!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
