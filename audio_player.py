#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مشغل الصوت البسيط لمعاينة ملفات Org 2024
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import threading
import time
from pathlib import Path
import os

class SimpleAudioPlayer:
    """مشغل صوت بسيط لمعاينة الملفات"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("مشغل الصوت - Org 2024")
        self.root.geometry("600x400")
        
        # تهيئة pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # متغيرات التطبيق
        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.duration = 0
        self.volume = 70
        
        # إعداد الواجهة
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # عنوان التطبيق
        title_label = ttk.Label(main_frame, text="مشغل الصوت - Org 2024", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # منطقة اختيار الملف
        file_frame = ttk.LabelFrame(main_frame, text="اختيار الملف", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(file_frame, text="تصفح", command=self.browse_file).pack(side=tk.LEFT)
        
        # معلومات الملف
        info_frame = ttk.LabelFrame(main_frame, text="معلومات الملف", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, width=70)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # أزرار التحكم
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        self.play_button = ttk.Button(control_frame, text="▶️ تشغيل", command=self.play_pause)
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="⏹️ إيقاف", command=self.stop).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏮️ السابق", command=self.previous_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏭️ التالي", command=self.next_file).pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(progress_frame, text="التقدم:").pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.time_label = ttk.Label(progress_frame, text="00:00 / 00:00")
        self.time_label.pack(side=tk.RIGHT)
        
        # التحكم في الصوت
        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(volume_frame, text="الصوت:").pack(side=tk.LEFT)
        self.volume_var = tk.DoubleVar(value=self.volume)
        volume_scale = ttk.Scale(volume_frame, from_=0, to=100, variable=self.volume_var, 
                                orient=tk.HORIZONTAL, command=self.change_volume)
        volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.volume_label = ttk.Label(volume_frame, text=f"{self.volume}%")
        self.volume_label.pack(side=tk.RIGHT)
        
        # قائمة الملفات
        playlist_frame = ttk.LabelFrame(main_frame, text="قائمة التشغيل", padding="10")
        playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # إطار للأزرار
        playlist_buttons = ttk.Frame(playlist_frame)
        playlist_buttons.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(playlist_buttons, text="إضافة مجلد", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_buttons, text="مسح القائمة", command=self.clear_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_buttons, text="حفظ القائمة", command=self.save_playlist).pack(side=tk.LEFT, padx=5)
        
        # قائمة الملفات
        self.playlist = tk.Listbox(playlist_frame, height=8)
        playlist_scrollbar = ttk.Scrollbar(playlist_frame, orient="vertical", command=self.playlist.yview)
        self.playlist.configure(yscrollcommand=playlist_scrollbar.set)
        
        self.playlist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ربط الأحداث
        self.playlist.bind('<Double-Button-1>', self.on_playlist_double_click)
        
        # بدء thread لتحديث التقدم
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()
    
    def browse_file(self):
        """تصفح ملف صوتي"""
        filetypes = [
            ("ملفات الصوت", "*.wav *.mp3 *.ogg *.flac"),
            ("ملفات WAV", "*.wav"),
            ("ملفات MP3", "*.mp3"),
            ("جميع الملفات", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="اختر ملف صوتي",
            filetypes=filetypes
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """تحميل ملف صوتي"""
        try:
            self.current_file = file_path
            
            # تحميل الملف
            pygame.mixer.music.load(file_path)
            
            # عرض معلومات الملف
            self.show_file_info(file_path)
            
            # إضافة إلى قائمة التشغيل إذا لم يكن موجوداً
            file_name = Path(file_path).name
            if file_name not in [self.playlist.get(i) for i in range(self.playlist.size())]:
                self.playlist.insert(tk.END, file_name)
            
            messagebox.showinfo("نجح", f"تم تحميل الملف: {Path(file_path).name}")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تحميل الملف: {str(e)}")
    
    def show_file_info(self, file_path):
        """عرض معلومات الملف"""
        self.info_text.delete(1.0, tk.END)
        
        try:
            file_path = Path(file_path)
            stat = file_path.stat()
            
            info = f"اسم الملف: {file_path.name}\n"
            info += f"المسار: {file_path.parent}\n"
            info += f"الحجم: {stat.st_size / (1024*1024):.2f} MB\n"
            info += f"النوع: {file_path.suffix.upper()}\n"
            info += f"تاريخ التعديل: {time.ctime(stat.st_mtime)}\n"
            
            # معلومات إضافية حسب نوع الملف
            if file_path.suffix.lower() == '.wav':
                info += self.get_wav_info(file_path)
            elif file_path.suffix.lower() == '.mp3':
                info += self.get_mp3_info(file_path)
            
            self.info_text.insert(1.0, info)
            
        except Exception as e:
            self.info_text.insert(1.0, f"خطأ في قراءة معلومات الملف: {str(e)}")
    
    def get_wav_info(self, file_path):
        """الحصول على معلومات ملف WAV"""
        try:
            import wave
            with wave.open(str(file_path), 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                duration = frames / sample_rate
                
                info = f"معدل العينة: {sample_rate} Hz\n"
                info += f"القنوات: {channels}\n"
                info += f"عرض العينة: {sample_width * 8} bit\n"
                info += f"المدة: {duration:.2f} ثانية\n"
                
                return info
        except:
            return "لا يمكن قراءة معلومات WAV\n"
    
    def get_mp3_info(self, file_path):
        """الحصول على معلومات ملف MP3"""
        try:
            # معلومات أساسية - يمكن تحسينها باستخدام مكتبات متخصصة
            return "ملف MP3 - استخدم مكتبة متخصصة للمعلومات التفصيلية\n"
        except:
            return "لا يمكن قراءة معلومات MP3\n"
    
    def play_pause(self):
        """تشغيل أو إيقاف مؤقت"""
        if not self.current_file:
            messagebox.showwarning("تحذير", "يرجى اختيار ملف أولاً")
            return
        
        try:
            if not self.is_playing:
                if self.is_paused:
                    pygame.mixer.music.unpause()
                    self.is_paused = False
                else:
                    pygame.mixer.music.play()
                
                self.is_playing = True
                self.play_button.config(text="⏸️ إيقاف مؤقت")
            
            else:
                pygame.mixer.music.pause()
                self.is_playing = False
                self.is_paused = True
                self.play_button.config(text="▶️ تشغيل")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في التشغيل: {str(e)}")
    
    def stop(self):
        """إيقاف التشغيل"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.position = 0
            self.progress_var.set(0)
            self.play_button.config(text="▶️ تشغيل")
            self.time_label.config(text="00:00 / 00:00")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"خطأ في الإيقاف: {str(e)}")
    
    def change_volume(self, value):
        """تغيير مستوى الصوت"""
        try:
            volume = float(value)
            pygame.mixer.music.set_volume(volume / 100.0)
            self.volume = volume
            self.volume_label.config(text=f"{int(volume)}%")
            
        except Exception as e:
            print(f"خطأ في تغيير الصوت: {str(e)}")
    
    def add_folder(self):
        """إضافة مجلد إلى قائمة التشغيل"""
        folder_path = filedialog.askdirectory(title="اختر مجلد الملفات الصوتية")
        
        if folder_path:
            try:
                folder = Path(folder_path)
                audio_extensions = ['.wav', '.mp3', '.ogg', '.flac']
                
                added_count = 0
                for ext in audio_extensions:
                    for file_path in folder.rglob(f"*{ext}"):
                        file_name = file_path.name
                        # تجنب الإضافة المكررة
                        if file_name not in [self.playlist.get(i) for i in range(self.playlist.size())]:
                            self.playlist.insert(tk.END, file_name)
                            added_count += 1
                
                messagebox.showinfo("نجح", f"تم إضافة {added_count} ملف إلى قائمة التشغيل")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في إضافة المجلد: {str(e)}")
    
    def clear_playlist(self):
        """مسح قائمة التشغيل"""
        self.playlist.delete(0, tk.END)
    
    def save_playlist(self):
        """حفظ قائمة التشغيل"""
        if self.playlist.size() == 0:
            messagebox.showwarning("تحذير", "قائمة التشغيل فارغة")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="حفظ قائمة التشغيل",
            defaultextension=".m3u",
            filetypes=[("M3U Playlist", "*.m3u"), ("Text Files", "*.txt")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for i in range(self.playlist.size()):
                        f.write(f"{self.playlist.get(i)}\n")
                
                messagebox.showinfo("نجح", "تم حفظ قائمة التشغيل")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في حفظ القائمة: {str(e)}")
    
    def on_playlist_double_click(self, event):
        """التعامل مع النقر المزدوج على قائمة التشغيل"""
        selection = self.playlist.curselection()
        if selection:
            file_name = self.playlist.get(selection[0])
            # البحث عن الملف في المجلد الحالي أو المجلدات المعروفة
            self.find_and_load_file(file_name)
    
    def find_and_load_file(self, file_name):
        """البحث عن الملف وتحميله"""
        # البحث في المجلد الحالي للملف المحمل
        if self.current_file:
            current_dir = Path(self.current_file).parent
            file_path = current_dir / file_name
            if file_path.exists():
                self.file_path_var.set(str(file_path))
                self.load_file(str(file_path))
                return
        
        # البحث في مجلدات شائعة
        common_dirs = [
            Path.home() / "Music",
            Path.home() / "Downloads",
            Path("/usr/share/org2024/Sounds"),
            Path("/opt/org2024/Sounds")
        ]
        
        for dir_path in common_dirs:
            if dir_path.exists():
                file_path = dir_path / file_name
                if file_path.exists():
                    self.file_path_var.set(str(file_path))
                    self.load_file(str(file_path))
                    return
        
        messagebox.showwarning("تحذير", f"لم يتم العثور على الملف: {file_name}")
    
    def previous_file(self):
        """الملف السابق في القائمة"""
        if self.playlist.size() == 0:
            return
        
        current_selection = self.playlist.curselection()
        if current_selection:
            prev_index = (current_selection[0] - 1) % self.playlist.size()
        else:
            prev_index = self.playlist.size() - 1
        
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(prev_index)
        self.playlist.see(prev_index)
        
        file_name = self.playlist.get(prev_index)
        self.find_and_load_file(file_name)
    
    def next_file(self):
        """الملف التالي في القائمة"""
        if self.playlist.size() == 0:
            return
        
        current_selection = self.playlist.curselection()
        if current_selection:
            next_index = (current_selection[0] + 1) % self.playlist.size()
        else:
            next_index = 0
        
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(next_index)
        self.playlist.see(next_index)
        
        file_name = self.playlist.get(next_index)
        self.find_and_load_file(file_name)
    
    def update_progress(self):
        """تحديث شريط التقدم"""
        while True:
            try:
                if self.is_playing and not self.is_paused:
                    # تحديث بسيط للوقت (pygame لا يدعم الحصول على الموضع الدقيق)
                    self.position += 1
                    
                    # تحديث شريط التقدم (تقدير تقريبي)
                    if self.duration > 0:
                        progress = (self.position / self.duration) * 100
                        self.progress_var.set(min(progress, 100))
                    
                    # تحديث تسمية الوقت
                    current_time = self.format_time(self.position)
                    total_time = self.format_time(self.duration) if self.duration > 0 else "00:00"
                    self.time_label.config(text=f"{current_time} / {total_time}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"خطأ في تحديث التقدم: {str(e)}")
                time.sleep(1)
    
    def format_time(self, seconds):
        """تنسيق الوقت"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

def main():
    root = tk.Tk()
    app = SimpleAudioPlayer(root)
    root.mainloop()

if __name__ == "__main__":
    main()