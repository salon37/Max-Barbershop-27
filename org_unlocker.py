#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Org 2024 Sound & Beat Unlocker
تطبيق لفتح قفل الإيقاعات والأصوات في Org 2024
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import subprocess
import json
from pathlib import Path
import threading
import time

class OrgUnlocker:
    def __init__(self, root):
        self.root = root
        self.root.title("Org 2024 Sound & Beat Unlocker")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # متغيرات التطبيق
        self.org_path = tk.StringVar()
        self.backup_path = tk.StringVar()
        self.status_var = tk.StringVar(value="جاهز للبدء")
        self.progress_var = tk.DoubleVar()
        
        # إعداد الواجهة
        self.setup_ui()
        
        # البحث التلقائي عن مسار Org
        self.auto_detect_org()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # عنوان التطبيق
        title_label = ttk.Label(main_frame, text="Org 2024 Sound & Beat Unlocker", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # مسار Org
        ttk.Label(main_frame, text="مسار تطبيق Org 2024:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.org_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="تصفح", command=self.browse_org_path).grid(row=1, column=2, padx=5, pady=5)
        
        # مسار النسخ الاحتياطي
        ttk.Label(main_frame, text="مجلد النسخ الاحتياطي:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.backup_path, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="تصفح", command=self.browse_backup_path).grid(row=2, column=2, padx=5, pady=5)
        
        # خيارات الفتح
        options_frame = ttk.LabelFrame(main_frame, text="خيارات الفتح", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        self.unlock_sounds = tk.BooleanVar(value=True)
        self.unlock_beats = tk.BooleanVar(value=True)
        self.create_backup = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="فتح قفل الأصوات", variable=self.unlock_sounds).grid(row=0, column=0, sticky=tk.W, padx=10)
        ttk.Checkbutton(options_frame, text="فتح قفل الإيقاعات", variable=self.unlock_beats).grid(row=0, column=1, sticky=tk.W, padx=10)
        ttk.Checkbutton(options_frame, text="إنشاء نسخة احتياطية", variable=self.create_backup).grid(row=0, column=2, sticky=tk.W, padx=10)
        
        # أزرار التحكم
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="فحص الملفات", command=self.scan_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="فتح الأقفال", command=self.unlock_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="استعادة النسخة الاحتياطية", command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        ttk.Label(main_frame, text="التقدم:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # شريط الحالة
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        ttk.Label(status_frame, text="الحالة:").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=10)
        
        # منطقة السجل
        log_frame = ttk.LabelFrame(main_frame, text="سجل العمليات", padding="5")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # تكوين الشبكة للتمدد
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def log_message(self, message):
        """إضافة رسالة إلى السجل"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def auto_detect_org(self):
        """البحث التلقائي عن مسار Org"""
        possible_paths = [
            "/usr/share/org2024",
            "/opt/org2024",
            os.path.expanduser("~/org2024"),
            "/usr/local/share/org2024",
            "/var/lib/org2024"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.org_path.set(path)
                self.log_message(f"تم العثور على Org في: {path}")
                break
        
        # تعيين مسار النسخ الاحتياطي الافتراضي
        backup_dir = os.path.expanduser("~/org2024_backup")
        self.backup_path.set(backup_dir)
    
    def browse_org_path(self):
        """تصفح مسار Org"""
        path = filedialog.askdirectory(title="اختر مجلد Org 2024")
        if path:
            self.org_path.set(path)
    
    def browse_backup_path(self):
        """تصفح مسار النسخ الاحتياطي"""
        path = filedialog.askdirectory(title="اختر مجلد النسخ الاحتياطي")
        if path:
            self.backup_path.set(path)
    
    def scan_files(self):
        """فحص الملفات المقفولة"""
        if not self.org_path.get():
            messagebox.showerror("خطأ", "يرجى تحديد مسار Org 2024")
            return
        
        self.status_var.set("جاري فحص الملفات...")
        self.log_message("بدء فحص الملفات المقفولة...")
        
        threading.Thread(target=self._scan_files_thread, daemon=True).start()
    
    def _scan_files_thread(self):
        """فحص الملفات في thread منفصل"""
        try:
            org_dir = Path(self.org_path.get())
            locked_files = []
            
            # البحث عن ملفات الصوت والإيقاعات المقفولة
            sound_extensions = ['.wav', '.mp3', '.ogg', '.flac']
            beat_extensions = ['.drm', '.sty', '.pat']
            
            total_files = 0
            processed_files = 0
            
            # حساب إجمالي الملفات
            for ext in sound_extensions + beat_extensions:
                total_files += len(list(org_dir.rglob(f"*{ext}")))
            
            # فحص الملفات
            for ext in sound_extensions + beat_extensions:
                for file_path in org_dir.rglob(f"*{ext}"):
                    if self._is_file_locked(file_path):
                        locked_files.append(file_path)
                        self.log_message(f"ملف مقفول: {file_path.name}")
                    
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    self.progress_var.set(progress)
            
            self.log_message(f"تم العثور على {len(locked_files)} ملف مقفول")
            self.status_var.set(f"تم فحص {total_files} ملف - {len(locked_files)} مقفول")
            
        except Exception as e:
            self.log_message(f"خطأ في الفحص: {str(e)}")
            self.status_var.set("خطأ في الفحص")
    
    def _is_file_locked(self, file_path):
        """فحص ما إذا كان الملف مقفولاً"""
        try:
            # فحص الصلاحيات
            if not os.access(file_path, os.R_OK):
                return True
            
            # فحص وجود ملفات القفل
            lock_file = file_path.with_suffix(file_path.suffix + '.lock')
            if lock_file.exists():
                return True
            
            # فحص البيانات الوصفية للقفل
            if file_path.stat().st_mode & 0o077 == 0:  # ملف للقراءة فقط
                return True
                
            return False
            
        except Exception:
            return True
    
    def unlock_files(self):
        """فتح أقفال الملفات"""
        if not self.org_path.get():
            messagebox.showerror("خطأ", "يرجى تحديد مسار Org 2024")
            return
        
        if self.create_backup.get() and not self.backup_path.get():
            messagebox.showerror("خطأ", "يرجى تحديد مسار النسخ الاحتياطي")
            return
        
        result = messagebox.askyesno("تأكيد", "هل أنت متأكد من فتح الأقفال؟\nيُنصح بإنشاء نسخة احتياطية أولاً")
        if not result:
            return
        
        self.status_var.set("جاري فتح الأقفال...")
        threading.Thread(target=self._unlock_files_thread, daemon=True).start()
    
    def _unlock_files_thread(self):
        """فتح الأقفال في thread منفصل"""
        try:
            org_dir = Path(self.org_path.get())
            
            # إنشاء نسخة احتياطية
            if self.create_backup.get():
                self.log_message("إنشاء نسخة احتياطية...")
                backup_dir = Path(self.backup_path.get())
                backup_dir.mkdir(exist_ok=True)
                
                # نسخ الملفات المهمة
                important_dirs = ['Sounds', 'Styles', 'Drums', 'Voices']
                for dir_name in important_dirs:
                    src_dir = org_dir / dir_name
                    if src_dir.exists():
                        dst_dir = backup_dir / dir_name
                        if dst_dir.exists():
                            shutil.rmtree(dst_dir)
                        shutil.copytree(src_dir, dst_dir)
                        self.log_message(f"تم نسخ: {dir_name}")
            
            # فتح أقفال الأصوات
            if self.unlock_sounds.get():
                self._unlock_sounds(org_dir)
            
            # فتح أقفال الإيقاعات
            if self.unlock_beats.get():
                self._unlock_beats(org_dir)
            
            self.log_message("تم الانتهاء من فتح الأقفال بنجاح!")
            self.status_var.set("تم فتح الأقفال بنجاح")
            messagebox.showinfo("نجح", "تم فتح الأقفال بنجاح!")
            
        except Exception as e:
            self.log_message(f"خطأ في فتح الأقفال: {str(e)}")
            self.status_var.set("خطأ في فتح الأقفال")
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def _unlock_sounds(self, org_dir):
        """فتح أقفال الأصوات"""
        self.log_message("فتح أقفال الأصوات...")
        
        sounds_dir = org_dir / "Sounds"
        if not sounds_dir.exists():
            return
        
        sound_files = list(sounds_dir.rglob("*.wav")) + list(sounds_dir.rglob("*.mp3"))
        total_files = len(sound_files)
        
        for i, sound_file in enumerate(sound_files):
            try:
                # تغيير صلاحيات الملف
                os.chmod(sound_file, 0o644)
                
                # إزالة ملفات القفل
                lock_file = sound_file.with_suffix(sound_file.suffix + '.lock')
                if lock_file.exists():
                    os.remove(lock_file)
                
                # تحديث شريط التقدم
                progress = (i + 1) / total_files * 50  # 50% للأصوات
                self.progress_var.set(progress)
                
            except Exception as e:
                self.log_message(f"خطأ في فتح قفل {sound_file.name}: {str(e)}")
        
        self.log_message(f"تم فتح قفل {total_files} ملف صوتي")
    
    def _unlock_beats(self, org_dir):
        """فتح أقفال الإيقاعات"""
        self.log_message("فتح أقفال الإيقاعات...")
        
        styles_dir = org_dir / "Styles"
        drums_dir = org_dir / "Drums"
        
        beat_files = []
        if styles_dir.exists():
            beat_files.extend(styles_dir.rglob("*.sty"))
        if drums_dir.exists():
            beat_files.extend(drums_dir.rglob("*.drm"))
        
        total_files = len(beat_files)
        
        for i, beat_file in enumerate(beat_files):
            try:
                # تغيير صلاحيات الملف
                os.chmod(beat_file, 0o644)
                
                # إزالة ملفات القفل
                lock_file = beat_file.with_suffix(beat_file.suffix + '.lock')
                if lock_file.exists():
                    os.remove(lock_file)
                
                # تحديث شريط التقدم
                progress = 50 + (i + 1) / total_files * 50  # 50% للإيقاعات
                self.progress_var.set(progress)
                
            except Exception as e:
                self.log_message(f"خطأ في فتح قفل {beat_file.name}: {str(e)}")
        
        self.log_message(f"تم فتح قفل {total_files} ملف إيقاع")
    
    def restore_backup(self):
        """استعادة النسخة الاحتياطية"""
        if not self.backup_path.get():
            messagebox.showerror("خطأ", "يرجى تحديد مسار النسخ الاحتياطي")
            return
        
        backup_dir = Path(self.backup_path.get())
        if not backup_dir.exists():
            messagebox.showerror("خطأ", "مجلد النسخ الاحتياطي غير موجود")
            return
        
        result = messagebox.askyesno("تأكيد", "هل أنت متأكد من استعادة النسخة الاحتياطية؟\nسيتم استبدال الملفات الحالية")
        if not result:
            return
        
        try:
            org_dir = Path(self.org_path.get())
            
            # استعادة المجلدات
            for backup_subdir in backup_dir.iterdir():
                if backup_subdir.is_dir():
                    target_dir = org_dir / backup_subdir.name
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    shutil.copytree(backup_subdir, target_dir)
                    self.log_message(f"تم استعادة: {backup_subdir.name}")
            
            messagebox.showinfo("نجح", "تم استعادة النسخة الاحتياطية بنجاح!")
            self.log_message("تم استعادة النسخة الاحتياطية بنجاح")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في الاستعادة: {str(e)}")
            self.log_message(f"خطأ في الاستعادة: {str(e)}")

def main():
    root = tk.Tk()
    app = OrgUnlocker(root)
    root.mainloop()

if __name__ == "__main__":
    main()