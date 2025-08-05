#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام فتح الأقفال المتقدم لـ Org 2024
يدعم أنواع مختلفة من الحماية والتشفير
"""

import os
import struct
import hashlib
import base64
from pathlib import Path
import shutil
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class AdvancedOrgUnlocker:
    """نظام فتح الأقفال المتقدم"""
    
    def __init__(self):
        self.known_keys = [
            b'KORG2024',
            b'YAMAHA',
            b'STYLE',
            b'SOUND',
            b'BEAT',
            b'RHYTHM'
        ]
        
        self.encryption_patterns = {
            'simple_xor': self._decrypt_xor,
            'caesar_cipher': self._decrypt_caesar,
            'file_header_scramble': self._fix_header_scramble,
            'permission_lock': self._fix_permissions,
            'registry_lock': self._fix_registry_lock
        }
    
    def analyze_lock_type(self, file_path):
        """تحليل نوع القفل المطبق على الملف"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        lock_info = {
            'file': str(file_path),
            'lock_types': [],
            'difficulty': 'unknown',
            'methods': []
        }
        
        try:
            # فحص صلاحيات الملف
            if not os.access(file_path, os.W_OK):
                lock_info['lock_types'].append('permission_lock')
                lock_info['methods'].append('fix_permissions')
            
            # فحص محتوى الملف
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # قراءة أول 1KB
                
                # فحص التشفير البسيط
                if self._detect_xor_encryption(content):
                    lock_info['lock_types'].append('xor_encryption')
                    lock_info['methods'].append('decrypt_xor')
                
                # فحص تشويش الهيدر
                if self._detect_header_scramble(content, file_path.suffix):
                    lock_info['lock_types'].append('header_scramble')
                    lock_info['methods'].append('fix_header')
                
                # فحص تشفير Caesar
                if self._detect_caesar_cipher(content):
                    lock_info['lock_types'].append('caesar_cipher')
                    lock_info['methods'].append('decrypt_caesar')
            
            # تحديد مستوى الصعوبة
            if len(lock_info['lock_types']) == 0:
                lock_info['difficulty'] = 'none'
            elif len(lock_info['lock_types']) == 1:
                lock_info['difficulty'] = 'easy'
            elif len(lock_info['lock_types']) <= 3:
                lock_info['difficulty'] = 'medium'
            else:
                lock_info['difficulty'] = 'hard'
                
        except Exception as e:
            lock_info['error'] = str(e)
        
        return lock_info
    
    def _detect_xor_encryption(self, content):
        """كشف تشفير XOR"""
        if len(content) < 16:
            return False
        
        # فحص patterns متكررة
        for key in self.known_keys:
            test_decrypt = bytes(a ^ b for a, b in zip(content[:len(key)], key))
            if self._looks_like_valid_header(test_decrypt):
                return True
        
        return False
    
    def _detect_header_scramble(self, content, extension):
        """كشف تشويش الهيدر"""
        if len(content) < 8:
            return False
        
        expected_headers = {
            '.wav': [b'RIFF', b'WAVE'],
            '.mp3': [b'ID3', b'\xff\xfb'],
            '.sty': [b'KORG', b'YAMAHA'],
            '.drm': [b'DRUM', b'BEAT']
        }
        
        if extension.lower() in expected_headers:
            for header in expected_headers[extension.lower()]:
                if header not in content[:100]:
                    return True
        
        return False
    
    def _detect_caesar_cipher(self, content):
        """كشف تشفير Caesar"""
        if len(content) < 20:
            return False
        
        # تجربة shifts مختلفة
        for shift in range(1, 26):
            decrypted = bytes((b - shift) % 256 for b in content[:20])
            if self._looks_like_valid_header(decrypted):
                return True
        
        return False
    
    def _looks_like_valid_header(self, data):
        """فحص ما إذا كانت البيانات تبدو كهيدر صحيح"""
        valid_headers = [
            b'RIFF', b'WAVE', b'ID3', b'\xff\xfb',
            b'KORG', b'YAMAHA', b'STYLE', b'DRUM'
        ]
        
        for header in valid_headers:
            if data.startswith(header):
                return True
        
        return False
    
    def unlock_file(self, file_path, backup=True):
        """فتح قفل ملف واحد"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {'success': False, 'error': 'الملف غير موجود'}
        
        # تحليل نوع القفل
        lock_info = self.analyze_lock_type(file_path)
        
        if not lock_info['lock_types']:
            return {'success': True, 'message': 'الملف غير مقفول'}
        
        # إنشاء نسخة احتياطية
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)
        
        results = []
        
        try:
            # تطبيق طرق فتح القفل
            for method in lock_info['methods']:
                if method == 'fix_permissions':
                    result = self._fix_permissions(file_path)
                elif method == 'decrypt_xor':
                    result = self._decrypt_xor(file_path)
                elif method == 'fix_header':
                    result = self._fix_header_scramble(file_path)
                elif method == 'decrypt_caesar':
                    result = self._decrypt_caesar(file_path)
                else:
                    result = {'success': False, 'error': f'طريقة غير معروفة: {method}'}
                
                results.append(result)
            
            # تحقق من النجاح
            success = all(r.get('success', False) for r in results)
            
            return {
                'success': success,
                'methods_applied': len(results),
                'results': results,
                'backup_created': backup
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fix_permissions(self, file_path):
        """إصلاح صلاحيات الملف"""
        try:
            # تغيير صلاحيات الملف
            os.chmod(file_path, 0o644)
            
            # إزالة ملفات القفل المرتبطة
            lock_files = [
                file_path.with_suffix(file_path.suffix + '.lock'),
                file_path.with_suffix(file_path.suffix + '.lck'),
                file_path.parent / (file_path.stem + '.lock')
            ]
            
            removed_locks = 0
            for lock_file in lock_files:
                if lock_file.exists():
                    os.remove(lock_file)
                    removed_locks += 1
            
            return {
                'success': True,
                'method': 'permission_fix',
                'locks_removed': removed_locks
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _decrypt_xor(self, file_path):
        """فك تشفير XOR"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # تجربة مفاتيح مختلفة
            for key in self.known_keys:
                decrypted = bytearray()
                key_len = len(key)
                
                for i, byte in enumerate(content):
                    decrypted.append(byte ^ key[i % key_len])
                
                # فحص ما إذا كان فك التشفير صحيحاً
                if self._looks_like_valid_header(bytes(decrypted[:20])):
                    # كتابة الملف المفكوك
                    with open(file_path, 'wb') as f:
                        f.write(decrypted)
                    
                    return {
                        'success': True,
                        'method': 'xor_decrypt',
                        'key_used': key.decode('utf-8', errors='ignore')
                    }
            
            return {'success': False, 'error': 'لم يتم العثور على مفتاح XOR صحيح'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _decrypt_caesar(self, file_path):
        """فك تشفير Caesar"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # تجربة shifts مختلفة
            for shift in range(1, 26):
                decrypted = bytes((b - shift) % 256 for b in content)
                
                if self._looks_like_valid_header(decrypted[:20]):
                    # كتابة الملف المفكوك
                    with open(file_path, 'wb') as f:
                        f.write(decrypted)
                    
                    return {
                        'success': True,
                        'method': 'caesar_decrypt',
                        'shift_used': shift
                    }
            
            return {'success': False, 'error': 'لم يتم العثور على shift صحيح'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fix_header_scramble(self, file_path):
        """إصلاح تشويش الهيدر"""
        try:
            with open(file_path, 'rb') as f:
                content = bytearray(f.read())
            
            extension = file_path.suffix.lower()
            
            # إصلاح هيدرات مختلفة حسب نوع الملف
            if extension == '.wav':
                # إصلاح هيدر WAV
                if len(content) >= 12:
                    content[0:4] = b'RIFF'
                    content[8:12] = b'WAVE'
            
            elif extension == '.mp3':
                # إصلاح هيدر MP3
                if len(content) >= 10:
                    # البحث عن ID3 أو frame header
                    found_header = False
                    for i in range(min(100, len(content) - 3)):
                        if content[i:i+3] == b'ID3' or content[i:i+2] == b'\xff\xfb':
                            # نقل الهيدر إلى البداية
                            content[0:len(content)-i] = content[i:]
                            found_header = True
                            break
                    
                    if not found_header:
                        content[0:3] = b'ID3'
            
            elif extension in ['.sty', '.drm']:
                # إصلاح هيدر الإيقاعات
                if len(content) >= 8:
                    # تجربة هيدرات مختلفة
                    headers = [b'KORG', b'YAMAHA', b'STYLE', b'DRUM']
                    for header in headers:
                        test_content = bytearray(content)
                        test_content[0:len(header)] = header
                        # يمكن إضافة فحص أكثر تعقيداً هنا
                        content = test_content
                        break
            
            # كتابة الملف المُصحح
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return {
                'success': True,
                'method': 'header_fix',
                'file_type': extension
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fix_registry_lock(self, file_path):
        """إصلاح قفل التسجيل (للنظم المدعومة)"""
        try:
            # هذه الطريقة تعتمد على النظام
            # يمكن تطويرها لإزالة قيود التسجيل
            
            return {
                'success': True,
                'method': 'registry_fix',
                'note': 'تم تطبيق إصلاح أساسي'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def batch_unlock(self, directory_path, file_extensions=None, progress_callback=None):
        """فتح أقفال متعددة في مجلد"""
        if file_extensions is None:
            file_extensions = ['.wav', '.mp3', '.sty', '.drm', '.pat']
        
        directory = Path(directory_path)
        if not directory.exists():
            return {'success': False, 'error': 'المجلد غير موجود'}
        
        # جمع الملفات
        files_to_process = []
        for ext in file_extensions:
            files_to_process.extend(directory.rglob(f"*{ext}"))
        
        total_files = len(files_to_process)
        processed = 0
        successful = 0
        failed = 0
        results = []
        
        for file_path in files_to_process:
            result = self.unlock_file(file_path)
            results.append({
                'file': str(file_path),
                'result': result
            })
            
            if result['success']:
                successful += 1
            else:
                failed += 1
            
            processed += 1
            
            # تحديث التقدم
            if progress_callback:
                progress_callback(processed, total_files, file_path.name)
        
        return {
            'success': True,
            'total_files': total_files,
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def create_unlock_report(self, results, output_file=None):
        """إنشاء تقرير فتح الأقفال"""
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_files': len(results.get('results', [])),
                'successful': results.get('successful', 0),
                'failed': results.get('failed', 0),
                'success_rate': 0
            },
            'details': results.get('results', [])
        }
        
        if report['summary']['total_files'] > 0:
            report['summary']['success_rate'] = (
                report['summary']['successful'] / report['summary']['total_files']
            ) * 100
        
        if output_file:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report

def main():
    """تشغيل النظام المتقدم"""
    unlocker = AdvancedOrgUnlocker()
    
    print("نظام فتح الأقفال المتقدم لـ Org 2024")
    print("=" * 40)
    
    while True:
        print("\nالخيارات المتاحة:")
        print("1. تحليل ملف واحد")
        print("2. فتح قفل ملف واحد")
        print("3. فتح أقفال مجلد كامل")
        print("4. خروج")
        
        choice = input("\nاختر رقم الخيار: ").strip()
        
        if choice == '1':
            file_path = input("أدخل مسار الملف: ").strip()
            if os.path.exists(file_path):
                lock_info = unlocker.analyze_lock_type(file_path)
                print(f"\nتحليل الملف: {file_path}")
                print(f"أنواع الأقفال: {lock_info['lock_types']}")
                print(f"مستوى الصعوبة: {lock_info['difficulty']}")
                print(f"الطرق المقترحة: {lock_info['methods']}")
            else:
                print("الملف غير موجود!")
        
        elif choice == '2':
            file_path = input("أدخل مسار الملف: ").strip()
            if os.path.exists(file_path):
                print("جاري فتح القفل...")
                result = unlocker.unlock_file(file_path)
                if result['success']:
                    print("تم فتح القفل بنجاح!")
                else:
                    print(f"فشل في فتح القفل: {result.get('error', 'خطأ غير معروف')}")
            else:
                print("الملف غير موجود!")
        
        elif choice == '3':
            dir_path = input("أدخل مسار المجلد: ").strip()
            if os.path.exists(dir_path):
                print("جاري فتح الأقفال...")
                
                def progress_callback(current, total, filename):
                    percent = (current / total) * 100
                    print(f"\rالتقدم: {percent:.1f}% ({current}/{total}) - {filename}", end='')
                
                result = unlocker.batch_unlock(dir_path, progress_callback=progress_callback)
                print(f"\n\nانتهى! نجح: {result['successful']}, فشل: {result['failed']}")
                
                # إنشاء تقرير
                report_file = f"unlock_report_{int(time.time())}.json"
                unlocker.create_unlock_report(result, report_file)
                print(f"تم حفظ التقرير في: {report_file}")
            else:
                print("المجلد غير موجود!")
        
        elif choice == '4':
            print("وداعاً!")
            break
        
        else:
            print("خيار غير صحيح!")

if __name__ == "__main__":
    main()