#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة تحليل ملفات Org 2024 المتقدمة
"""

import os
import struct
import hashlib
from pathlib import Path
import json

class OrgFileAnalyzer:
    """محلل ملفات Org 2024"""
    
    def __init__(self):
        self.sound_signatures = {
            b'RIFF': 'WAV',
            b'ID3': 'MP3',
            b'\xff\xfb': 'MP3',
            b'OggS': 'OGG',
            b'fLaC': 'FLAC'
        }
        
        self.style_signatures = {
            b'KORG': 'Korg Style',
            b'YAMAHA': 'Yamaha Style',
            b'STYLE': 'Generic Style'
        }
    
    def analyze_file(self, file_path):
        """تحليل ملف واحد"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        analysis = {
            'path': str(file_path),
            'name': file_path.name,
            'size': file_path.stat().st_size,
            'extension': file_path.suffix.lower(),
            'is_locked': self._check_if_locked(file_path),
            'file_type': None,
            'format_info': {},
            'hash': None
        }
        
        # حساب hash للملف
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                analysis['hash'] = hashlib.md5(content).hexdigest()
                analysis['file_type'] = self._detect_file_type(content)
                analysis['format_info'] = self._analyze_format(content, file_path.suffix)
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _check_if_locked(self, file_path):
        """فحص ما إذا كان الملف مقفولاً"""
        try:
            # فحص الصلاحيات
            if not os.access(file_path, os.W_OK):
                return True
            
            # فحص وجود ملفات القفل
            lock_extensions = ['.lock', '.lck', '.tmp']
            for ext in lock_extensions:
                if (file_path.parent / (file_path.name + ext)).exists():
                    return True
            
            # فحص البيانات الوصفية
            stat = file_path.stat()
            if stat.st_mode & 0o200 == 0:  # لا يمكن الكتابة
                return True
                
            return False
        except:
            return True
    
    def _detect_file_type(self, content):
        """تحديد نوع الملف من محتواه"""
        if len(content) < 4:
            return 'Unknown'
        
        header = content[:4]
        
        # فحص ملفات الصوت
        for signature, file_type in self.sound_signatures.items():
            if content.startswith(signature):
                return file_type
        
        # فحص ملفات الإيقاعات
        for signature, file_type in self.style_signatures.items():
            if signature in content[:100]:  # البحث في أول 100 بايت
                return file_type
        
        return 'Unknown'
    
    def _analyze_format(self, content, extension):
        """تحليل تفاصيل تنسيق الملف"""
        info = {}
        
        try:
            if extension in ['.wav']:
                info = self._analyze_wav(content)
            elif extension in ['.mp3']:
                info = self._analyze_mp3(content)
            elif extension in ['.sty']:
                info = self._analyze_style(content)
            elif extension in ['.drm']:
                info = self._analyze_drum(content)
        except Exception as e:
            info['analysis_error'] = str(e)
        
        return info
    
    def _analyze_wav(self, content):
        """تحليل ملف WAV"""
        if len(content) < 44:
            return {'error': 'ملف WAV غير مكتمل'}
        
        try:
            # قراءة header الـ WAV
            riff = content[0:4]
            file_size = struct.unpack('<I', content[4:8])[0]
            wave = content[8:12]
            fmt_chunk = content[12:16]
            fmt_size = struct.unpack('<I', content[16:20])[0]
            audio_format = struct.unpack('<H', content[20:22])[0]
            channels = struct.unpack('<H', content[22:24])[0]
            sample_rate = struct.unpack('<I', content[24:28])[0]
            byte_rate = struct.unpack('<I', content[28:32])[0]
            block_align = struct.unpack('<H', content[32:34])[0]
            bits_per_sample = struct.unpack('<H', content[34:36])[0]
            
            return {
                'format': 'WAV',
                'channels': channels,
                'sample_rate': sample_rate,
                'bits_per_sample': bits_per_sample,
                'duration_seconds': file_size / byte_rate if byte_rate > 0 else 0,
                'audio_format': 'PCM' if audio_format == 1 else f'Format {audio_format}'
            }
        except:
            return {'error': 'خطأ في تحليل WAV'}
    
    def _analyze_mp3(self, content):
        """تحليل ملف MP3"""
        info = {'format': 'MP3'}
        
        try:
            # البحث عن ID3 tag
            if content.startswith(b'ID3'):
                version = content[3:5]
                info['id3_version'] = f"2.{version[0]}.{version[1]}"
                
                # حجم ID3 tag
                size_bytes = content[6:10]
                size = 0
                for byte in size_bytes:
                    size = (size << 7) | (byte & 0x7F)
                info['id3_size'] = size
            
            # البحث عن MP3 frame header
            for i in range(min(1000, len(content) - 4)):
                if content[i:i+2] == b'\xff\xfb' or content[i:i+2] == b'\xff\xfa':
                    frame_header = struct.unpack('>I', content[i:i+4])[0]
                    
                    # استخراج معلومات الإطار
                    version = (frame_header >> 19) & 3
                    layer = (frame_header >> 17) & 3
                    bitrate_index = (frame_header >> 12) & 15
                    sample_rate_index = (frame_header >> 10) & 3
                    
                    info['mpeg_version'] = version
                    info['layer'] = 4 - layer
                    break
                    
        except:
            info['error'] = 'خطأ في تحليل MP3'
        
        return info
    
    def _analyze_style(self, content):
        """تحليل ملف Style"""
        info = {'format': 'Style File'}
        
        try:
            # البحث عن معلومات الإيقاع
            if b'KORG' in content[:100]:
                info['manufacturer'] = 'Korg'
            elif b'YAMAHA' in content[:100]:
                info['manufacturer'] = 'Yamaha'
            
            # محاولة استخراج اسم الإيقاع
            for i in range(min(200, len(content) - 20)):
                chunk = content[i:i+20]
                if chunk.isascii():
                    try:
                        text = chunk.decode('ascii').strip('\x00')
                        if len(text) > 3 and text.isalnum():
                            info['style_name'] = text
                            break
                    except:
                        continue
                        
        except:
            info['error'] = 'خطأ في تحليل Style'
        
        return info
    
    def _analyze_drum(self, content):
        """تحليل ملف Drum"""
        info = {'format': 'Drum File'}
        
        try:
            # تحليل أساسي لملف الطبول
            info['size'] = len(content)
            
            # البحث عن patterns
            pattern_count = 0
            for i in range(0, len(content) - 4, 4):
                chunk = content[i:i+4]
                if all(b != 0 for b in chunk):  # نمط محتمل
                    pattern_count += 1
            
            info['estimated_patterns'] = pattern_count // 100  # تقدير تقريبي
            
        except:
            info['error'] = 'خطأ في تحليل Drum'
        
        return info
    
    def scan_directory(self, directory_path, extensions=None):
        """مسح مجلد كامل"""
        if extensions is None:
            extensions = ['.wav', '.mp3', '.ogg', '.flac', '.sty', '.drm', '.pat']
        
        results = []
        directory = Path(directory_path)
        
        if not directory.exists():
            return results
        
        for ext in extensions:
            for file_path in directory.rglob(f"*{ext}"):
                analysis = self.analyze_file(file_path)
                if analysis:
                    results.append(analysis)
        
        return results
    
    def generate_report(self, scan_results, output_file=None):
        """إنشاء تقرير تفصيلي"""
        report = {
            'total_files': len(scan_results),
            'locked_files': sum(1 for r in scan_results if r.get('is_locked', False)),
            'file_types': {},
            'total_size': sum(r.get('size', 0) for r in scan_results),
            'files': scan_results
        }
        
        # تجميع الملفات حسب النوع
        for result in scan_results:
            file_type = result.get('file_type', 'Unknown')
            if file_type not in report['file_types']:
                report['file_types'][file_type] = 0
            report['file_types'][file_type] += 1
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report

def main():
    """تشغيل المحلل"""
    analyzer = OrgFileAnalyzer()
    
    # مثال على الاستخدام
    org_path = input("أدخل مسار مجلد Org 2024: ").strip()
    
    if not org_path or not os.path.exists(org_path):
        print("المسار غير صحيح!")
        return
    
    print("جاري المسح...")
    results = analyzer.scan_directory(org_path)
    
    print(f"تم العثور على {len(results)} ملف")
    
    # إنشاء تقرير
    report = analyzer.generate_report(results, "org_analysis_report.json")
    
    print(f"إجمالي الملفات: {report['total_files']}")
    print(f"الملفات المقفولة: {report['locked_files']}")
    print(f"الحجم الإجمالي: {report['total_size'] / (1024*1024):.2f} MB")
    print("\nأنواع الملفات:")
    for file_type, count in report['file_types'].items():
        print(f"  {file_type}: {count}")
    
    print("\nتم حفظ التقرير في: org_analysis_report.json")

if __name__ == "__main__":
    main()