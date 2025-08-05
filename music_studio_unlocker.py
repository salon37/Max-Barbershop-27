#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music Studio 3 Unlocker Tool
أداة فتح قفل Music Studio 3 من Xewton
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import json
import sqlite3
import hashlib
from pathlib import Path
import threading
import time
import subprocess

class MusicStudioUnlocker:
    """أداة فتح قفل Music Studio 3"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Music Studio 3 Unlocker Tool")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        
        # متغيرات التطبيق
        self.app_path = tk.StringVar()
        self.backup_path = tk.StringVar()
        self.status_var = tk.StringVar(value="جاهز للبدء")
        self.progress_var = tk.DoubleVar()
        
        # معلومات Music Studio
        self.music_studio_info = {
            'package_name': 'com.xewton.musicstudio',
            'data_path': '/data/data/com.xewton.musicstudio/',
            'instruments_file': 'instruments.db',
            'sounds_folder': 'sounds/',
            'presets_folder': 'presets/',
            'locked_instruments': [
                'Piano Grand', 'Strings Ensemble', 'Guitar Electric',
                'Bass Synth', 'Drums Rock', 'Saxophone', 'Violin',
                'Trumpet', 'Flute', 'Organ Hammond'
            ]
        }
        
        # إعداد الواجهة
        self.setup_ui()
        
        # البحث التلقائي عن التطبيق
        self.auto_detect_app()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # إنشاء style مخصص
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='white', background='#1a1a1a')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#4CAF50')
        
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # عنوان التطبيق
        title_label = ttk.Label(main_frame, text="🎵 Music Studio 3 Unlocker Tool 🎵", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # معلومات التطبيق
        info_frame = ttk.LabelFrame(main_frame, text="معلومات Music Studio 3", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_text = """
        🎼 Music Studio 3 - أداة إنتاج موسيقي متقدمة
        📱 يحتوي على 178 آلة موسيقية مسجلة بجودة عالية
        🔒 118 آلة مجانية + 60 آلة مقفولة (تتطلب شراء)
        🎹 6 فئات: سيمفونية، كلاسيكية، فرقة، إلكترونية، عالمية، طبول
        """
        ttk.Label(info_frame, text=info_text, font=('Arial', 10)).pack()
        
        # مسار التطبيق
        path_frame = ttk.LabelFrame(main_frame, text="إعدادات المسار", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(path_frame, text="مسار تطبيق Music Studio 3:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(path_frame, textvariable=self.app_path, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(path_frame, text="تصفح", command=self.browse_app_path).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(path_frame, text="مجلد النسخ الاحتياطي:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(path_frame, textvariable=self.backup_path, width=60).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(path_frame, text="تصفح", command=self.browse_backup_path).grid(row=1, column=2, padx=5, pady=5)
        
        path_frame.columnconfigure(1, weight=1)
        
        # خيارات الفتح
        options_frame = ttk.LabelFrame(main_frame, text="خيارات فتح القفل", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.unlock_instruments = tk.BooleanVar(value=True)
        self.unlock_sounds = tk.BooleanVar(value=True)
        self.unlock_presets = tk.BooleanVar(value=True)
        self.unlock_effects = tk.BooleanVar(value=True)
        self.create_backup = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="🎹 فتح قفل الآلات الموسيقية (60 آلة)", 
                       variable=self.unlock_instruments).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Checkbutton(options_frame, text="🔊 فتح قفل الأصوات والعينات", 
                       variable=self.unlock_sounds).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Checkbutton(options_frame, text="🎛️ فتح قفل الإعدادات المسبقة", 
                       variable=self.unlock_presets).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        ttk.Checkbutton(options_frame, text="🎚️ فتح قفل التأثيرات الصوتية", 
                       variable=self.unlock_effects).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        ttk.Checkbutton(options_frame, text="💾 إنشاء نسخة احتياطية", 
                       variable=self.create_backup).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        # أزرار التحكم
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=15)
        
        ttk.Button(buttons_frame, text="🔍 فحص التطبيق", command=self.scan_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔓 فتح الأقفال", command=self.unlock_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔄 استعادة النسخة الاحتياطية", command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📊 تقرير مفصل", command=self.generate_report).pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(progress_frame, text="التقدم:", style='Header.TLabel').pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # شريط الحالة
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(status_frame, text="الحالة:", style='Header.TLabel').pack(side=tk.LEFT)
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=10)
        
        # منطقة السجل
        log_frame = ttk.LabelFrame(main_frame, text="سجل العمليات", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        self.log_text = tk.Text(log_frame, height=12, width=80, bg='#2b2b2b', fg='#ffffff', 
                               font=('Consolas', 10))
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # إضافة بعض النصائح
        self.log_message("🚀 مرحباً بك في أداة فتح قفل Music Studio 3!")
        self.log_message("💡 نصيحة: تأكد من إغلاق تطبيق Music Studio قبل البدء")
        self.log_message("⚠️ تحذير: قم بإنشاء نسخة احتياطية دائماً قبل التعديل")
    
    def log_message(self, message):
        """إضافة رسالة إلى السجل"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def auto_detect_app(self):
        """البحث التلقائي عن Music Studio"""
        possible_paths = [
            "/data/data/com.xewton.musicstudio/",
            "/storage/emulated/0/Android/data/com.xewton.musicstudio/",
            "/sdcard/Android/data/com.xewton.musicstudio/",
            os.path.expanduser("~/Music Studio/"),
            "/opt/musicstudio/",
            "/usr/share/musicstudio/"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.app_path.set(path)
                self.log_message(f"✅ تم العثور على Music Studio في: {path}")
                break
        else:
            self.log_message("❌ لم يتم العثور على Music Studio تلقائياً")
        
        # تعيين مسار النسخ الاحتياطي الافتراضي
        backup_dir = os.path.expanduser("~/music_studio_backup")
        self.backup_path.set(backup_dir)
    
    def browse_app_path(self):
        """تصفح مسار التطبيق"""
        path = filedialog.askdirectory(title="اختر مجلد Music Studio 3")
        if path:
            self.app_path.set(path)
            self.log_message(f"📁 تم تحديد المسار: {path}")
    
    def browse_backup_path(self):
        """تصفح مسار النسخ الاحتياطي"""
        path = filedialog.askdirectory(title="اختر مجلد النسخ الاحتياطي")
        if path:
            self.backup_path.set(path)
    
    def scan_app(self):
        """فحص التطبيق وتحليل الملفات المقفولة"""
        if not self.app_path.get():
            messagebox.showerror("خطأ", "يرجى تحديد مسار Music Studio 3")
            return
        
        self.status_var.set("جاري فحص التطبيق...")
        self.log_message("🔍 بدء فحص Music Studio 3...")
        
        threading.Thread(target=self._scan_app_thread, daemon=True).start()
    
    def _scan_app_thread(self):
        """فحص التطبيق في thread منفصل"""
        try:
            app_dir = Path(self.app_path.get())
            scan_results = {
                'locked_instruments': [],
                'locked_sounds': [],
                'locked_presets': [],
                'locked_effects': [],
                'total_files': 0
            }
            
            # فحص قاعدة بيانات الآلات
            db_path = app_dir / 'databases' / 'instruments.db'
            if db_path.exists():
                locked_instruments = self._scan_instruments_db(db_path)
                scan_results['locked_instruments'] = locked_instruments
                self.log_message(f"🎹 تم العثور على {len(locked_instruments)} آلة مقفولة")
            
            # فحص ملفات الأصوات
            sounds_dir = app_dir / 'files' / 'sounds'
            if sounds_dir.exists():
                locked_sounds = self._scan_locked_files(sounds_dir, ['.wav', '.mp3', '.ogg'])
                scan_results['locked_sounds'] = locked_sounds
                self.log_message(f"🔊 تم العثور على {len(locked_sounds)} ملف صوتي مقفول")
            
            # فحص الإعدادات المسبقة
            presets_dir = app_dir / 'files' / 'presets'
            if presets_dir.exists():
                locked_presets = self._scan_locked_files(presets_dir, ['.preset', '.json'])
                scan_results['locked_presets'] = locked_presets
                self.log_message(f"🎛️ تم العثور على {len(locked_presets)} إعداد مسبق مقفول")
            
            # فحص التأثيرات
            effects_dir = app_dir / 'files' / 'effects'
            if effects_dir.exists():
                locked_effects = self._scan_locked_files(effects_dir, ['.fx', '.effect'])
                scan_results['locked_effects'] = locked_effects
                self.log_message(f"🎚️ تم العثور على {len(locked_effects)} تأثير مقفول")
            
            total_locked = (len(scan_results['locked_instruments']) + 
                          len(scan_results['locked_sounds']) + 
                          len(scan_results['locked_presets']) + 
                          len(scan_results['locked_effects']))
            
            self.log_message(f"📊 إجمالي العناصر المقفولة: {total_locked}")
            self.status_var.set(f"تم الفحص - {total_locked} عنصر مقفول")
            
            # حفظ نتائج الفحص
            self.scan_results = scan_results
            
        except Exception as e:
            self.log_message(f"❌ خطأ في الفحص: {str(e)}")
            self.status_var.set("خطأ في الفحص")
    
    def _scan_instruments_db(self, db_path):
        """فحص قاعدة بيانات الآلات"""
        locked_instruments = []
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # البحث عن الآلات المقفولة
            cursor.execute("SELECT name, is_locked, price FROM instruments WHERE is_locked = 1")
            results = cursor.fetchall()
            
            for name, is_locked, price in results:
                locked_instruments.append({
                    'name': name,
                    'price': price,
                    'type': 'instrument'
                })
            
            conn.close()
        except Exception as e:
            self.log_message(f"❌ خطأ في قراءة قاعدة البيانات: {str(e)}")
        
        return locked_instruments
    
    def _scan_locked_files(self, directory, extensions):
        """فحص الملفات المقفولة في مجلد"""
        locked_files = []
        try:
            for ext in extensions:
                for file_path in directory.rglob(f"*{ext}"):
                    if self._is_file_locked(file_path):
                        locked_files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'size': file_path.stat().st_size,
                            'type': 'file'
                        })
        except Exception as e:
            self.log_message(f"❌ خطأ في فحص الملفات: {str(e)}")
        
        return locked_files
    
    def _is_file_locked(self, file_path):
        """فحص ما إذا كان الملف مقفولاً"""
        try:
            # فحص وجود ملف .lock
            lock_file = file_path.with_suffix(file_path.suffix + '.lock')
            if lock_file.exists():
                return True
            
            # فحص البيانات الوصفية
            with open(file_path, 'rb') as f:
                header = f.read(16)
                # البحث عن علامات القفل
                if b'LOCKED' in header or b'PREMIUM' in header:
                    return True
            
            # فحص الصلاحيات
            if not os.access(file_path, os.R_OK):
                return True
                
            return False
        except:
            return True
    
    def unlock_app(self):
        """فتح أقفال التطبيق"""
        if not self.app_path.get():
            messagebox.showerror("خطأ", "يرجى تحديد مسار Music Studio 3")
            return
        
        if not hasattr(self, 'scan_results'):
            messagebox.showwarning("تحذير", "يرجى فحص التطبيق أولاً")
            return
        
        result = messagebox.askyesno("تأكيد", 
                                   "هل أنت متأكد من فتح الأقفال؟\n"
                                   "سيتم تعديل ملفات التطبيق.\n"
                                   "تأكد من إنشاء نسخة احتياطية أولاً!")
        if not result:
            return
        
        self.status_var.set("جاري فتح الأقفال...")
        threading.Thread(target=self._unlock_app_thread, daemon=True).start()
    
    def _unlock_app_thread(self):
        """فتح الأقفال في thread منفصل"""
        try:
            app_dir = Path(self.app_path.get())
            
            # إنشاء نسخة احتياطية
            if self.create_backup.get():
                self.log_message("💾 إنشاء نسخة احتياطية...")
                self._create_backup(app_dir)
            
            unlock_count = 0
            total_items = 0
            
            # حساب إجمالي العناصر
            if hasattr(self, 'scan_results'):
                total_items = (len(self.scan_results.get('locked_instruments', [])) +
                             len(self.scan_results.get('locked_sounds', [])) +
                             len(self.scan_results.get('locked_presets', [])) +
                             len(self.scan_results.get('locked_effects', [])))
            
            # فتح قفل الآلات
            if self.unlock_instruments.get() and hasattr(self, 'scan_results'):
                self.log_message("🎹 فتح قفل الآلات الموسيقية...")
                count = self._unlock_instruments(app_dir)
                unlock_count += count
                self.log_message(f"✅ تم فتح قفل {count} آلة موسيقية")
            
            # فتح قفل الأصوات
            if self.unlock_sounds.get():
                self.log_message("🔊 فتح قفل الأصوات...")
                count = self._unlock_sounds(app_dir)
                unlock_count += count
                self.log_message(f"✅ تم فتح قفل {count} ملف صوتي")
            
            # فتح قفل الإعدادات المسبقة
            if self.unlock_presets.get():
                self.log_message("🎛️ فتح قفل الإعدادات المسبقة...")
                count = self._unlock_presets(app_dir)
                unlock_count += count
                self.log_message(f"✅ تم فتح قفل {count} إعداد مسبق")
            
            # فتح قفل التأثيرات
            if self.unlock_effects.get():
                self.log_message("🎚️ فتح قفل التأثيرات...")
                count = self._unlock_effects(app_dir)
                unlock_count += count
                self.log_message(f"✅ تم فتح قفل {count} تأثير")
            
            self.progress_var.set(100)
            self.log_message(f"🎉 تم الانتهاء! تم فتح قفل {unlock_count} عنصر بنجاح")
            self.status_var.set(f"تم فتح {unlock_count} عنصر بنجاح")
            
            messagebox.showinfo("نجح!", f"تم فتح قفل {unlock_count} عنصر بنجاح!\n"
                                      "يمكنك الآن الاستمتاع بجميع ميزات Music Studio 3")
            
        except Exception as e:
            self.log_message(f"❌ خطأ في فتح الأقفال: {str(e)}")
            self.status_var.set("خطأ في فتح الأقفال")
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def _create_backup(self, app_dir):
        """إنشاء نسخة احتياطية"""
        try:
            backup_dir = Path(self.backup_path.get())
            backup_dir.mkdir(exist_ok=True)
            
            # نسخ الملفات المهمة
            important_files = [
                'databases/instruments.db',
                'files/sounds/',
                'files/presets/',
                'files/effects/'
            ]
            
            for file_path in important_files:
                src = app_dir / file_path
                dst = backup_dir / file_path
                
                if src.exists():
                    if src.is_file():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                    else:
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    
                    self.log_message(f"💾 تم نسخ: {file_path}")
            
        except Exception as e:
            self.log_message(f"❌ خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
    
    def _unlock_instruments(self, app_dir):
        """فتح قفل الآلات الموسيقية"""
        try:
            db_path = app_dir / 'databases' / 'instruments.db'
            if not db_path.exists():
                return 0
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # فتح قفل جميع الآلات
            cursor.execute("UPDATE instruments SET is_locked = 0, price = 0 WHERE is_locked = 1")
            count = cursor.rowcount
            
            # إضافة الآلات المفقودة
            for instrument in self.music_studio_info['locked_instruments']:
                cursor.execute("INSERT OR IGNORE INTO instruments (name, is_locked, price) VALUES (?, 0, 0)", 
                             (instrument,))
            
            conn.commit()
            conn.close()
            
            return count
            
        except Exception as e:
            self.log_message(f"❌ خطأ في فتح قفل الآلات: {str(e)}")
            return 0
    
    def _unlock_sounds(self, app_dir):
        """فتح قفل الأصوات"""
        try:
            sounds_dir = app_dir / 'files' / 'sounds'
            if not sounds_dir.exists():
                return 0
            
            count = 0
            for file_path in sounds_dir.rglob("*"):
                if file_path.is_file() and self._unlock_file(file_path):
                    count += 1
            
            return count
            
        except Exception as e:
            self.log_message(f"❌ خطأ في فتح قفل الأصوات: {str(e)}")
            return 0
    
    def _unlock_presets(self, app_dir):
        """فتح قفل الإعدادات المسبقة"""
        try:
            presets_dir = app_dir / 'files' / 'presets'
            if not presets_dir.exists():
                return 0
            
            count = 0
            for file_path in presets_dir.rglob("*.preset"):
                if self._unlock_preset_file(file_path):
                    count += 1
            
            return count
            
        except Exception as e:
            self.log_message(f"❌ خطأ في فتح قفل الإعدادات: {str(e)}")
            return 0
    
    def _unlock_effects(self, app_dir):
        """فتح قفل التأثيرات"""
        try:
            effects_dir = app_dir / 'files' / 'effects'
            if not effects_dir.exists():
                return 0
            
            count = 0
            for file_path in effects_dir.rglob("*"):
                if file_path.is_file() and self._unlock_file(file_path):
                    count += 1
            
            return count
            
        except Exception as e:
            self.log_message(f"❌ خطأ في فتح قفل التأثيرات: {str(e)}")
            return 0
    
    def _unlock_file(self, file_path):
        """فتح قفل ملف واحد"""
        try:
            # إزالة ملف القفل
            lock_file = file_path.with_suffix(file_path.suffix + '.lock')
            if lock_file.exists():
                os.remove(lock_file)
            
            # تغيير صلاحيات الملف
            os.chmod(file_path, 0o644)
            
            # إزالة علامات القفل من الملف
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # استبدال علامات القفل
            content = content.replace(b'LOCKED', b'UNLOCK')
            content = content.replace(b'PREMIUM', b'FREEMUM')
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return True
            
        except Exception:
            return False
    
    def _unlock_preset_file(self, file_path):
        """فتح قفل ملف إعداد مسبق"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # تعديل حالة القفل
            if 'locked' in data:
                data['locked'] = False
            if 'premium' in data:
                data['premium'] = False
            if 'price' in data:
                data['price'] = 0.0
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def restore_backup(self):
        """استعادة النسخة الاحتياطية"""
        if not self.backup_path.get():
            messagebox.showerror("خطأ", "يرجى تحديد مسار النسخ الاحتياطي")
            return
        
        backup_dir = Path(self.backup_path.get())
        if not backup_dir.exists():
            messagebox.showerror("خطأ", "مجلد النسخ الاحتياطي غير موجود")
            return
        
        result = messagebox.askyesno("تأكيد", 
                                   "هل أنت متأكد من استعادة النسخة الاحتياطية؟\n"
                                   "سيتم استبدال الملفات الحالية")
        if not result:
            return
        
        try:
            app_dir = Path(self.app_path.get())
            
            # استعادة الملفات
            for backup_item in backup_dir.rglob("*"):
                if backup_item.is_file():
                    relative_path = backup_item.relative_to(backup_dir)
                    target_path = app_dir / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_item, target_path)
                    self.log_message(f"🔄 تم استعادة: {relative_path}")
            
            messagebox.showinfo("نجح", "تم استعادة النسخة الاحتياطية بنجاح!")
            self.log_message("✅ تم استعادة النسخة الاحتياطية بنجاح")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في الاستعادة: {str(e)}")
            self.log_message(f"❌ خطأ في الاستعادة: {str(e)}")
    
    def generate_report(self):
        """إنشاء تقرير مفصل"""
        if not hasattr(self, 'scan_results'):
            messagebox.showwarning("تحذير", "يرجى فحص التطبيق أولاً")
            return
        
        report_file = filedialog.asksaveasfilename(
            title="حفظ التقرير",
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("Text Files", "*.txt")]
        )
        
        if report_file:
            try:
                self._create_html_report(report_file)
                messagebox.showinfo("نجح", f"تم حفظ التقرير في:\n{report_file}")
                
                # فتح التقرير في المتصفح
                if messagebox.askyesno("فتح التقرير", "هل تريد فتح التقرير في المتصفح؟"):
                    subprocess.run(['xdg-open', report_file], check=False)
                    
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في إنشاء التقرير: {str(e)}")
    
    def _create_html_report(self, report_file):
        """إنشاء تقرير HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تقرير Music Studio 3 Unlocker</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 10px; }}
                .section {{ background: white; margin: 20px 0; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .item {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-right: 4px solid #4CAF50; }}
                .locked {{ border-right-color: #f44336; }}
                .stats {{ display: flex; justify-content: space-around; text-align: center; }}
                .stat {{ background: #e3f2fd; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎵 تقرير Music Studio 3 Unlocker</h1>
                <p>تاريخ الإنشاء: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 إحصائيات عامة</h2>
                <div class="stats">
                    <div class="stat">
                        <h3>{len(self.scan_results.get('locked_instruments', []))}</h3>
                        <p>آلة مقفولة</p>
                    </div>
                    <div class="stat">
                        <h3>{len(self.scan_results.get('locked_sounds', []))}</h3>
                        <p>ملف صوتي مقفول</p>
                    </div>
                    <div class="stat">
                        <h3>{len(self.scan_results.get('locked_presets', []))}</h3>
                        <p>إعداد مسبق مقفول</p>
                    </div>
                    <div class="stat">
                        <h3>{len(self.scan_results.get('locked_effects', []))}</h3>
                        <p>تأثير مقفول</p>
                    </div>
                </div>
            </div>
        """
        
        # إضافة تفاصيل الآلات
        if self.scan_results.get('locked_instruments'):
            html_content += """
            <div class="section">
                <h2>🎹 الآلات المقفولة</h2>
            """
            for instrument in self.scan_results['locked_instruments']:
                html_content += f"""
                <div class="item locked">
                    <strong>{instrument['name']}</strong>
                    <br>السعر: ${instrument.get('price', 'غير محدد')}
                </div>
                """
            html_content += "</div>"
        
        html_content += """
            <div class="section">
                <h2>ℹ️ معلومات إضافية</h2>
                <p>🔧 هذا التقرير تم إنشاؤه بواسطة Music Studio 3 Unlocker Tool</p>
                <p>⚠️ تأكد من إنشاء نسخة احتياطية قبل إجراء أي تعديل</p>
                <p>📱 Music Studio 3 هو تطبيق إنتاج موسيقي متقدم من Xewton</p>
            </div>
        </body>
        </html>
        """
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

def main():
    root = tk.Tk()
    app = MusicStudioUnlocker(root)
    root.mainloop()

if __name__ == "__main__":
    main()