[app]
# (str) عنوان برنامه
title = TileExplorer

# (str) نام بسته
package.name = tileexplorer

# (str) دامنه بسته
package.domain = org.tileexplorer

# (str) مسیر پوشه منبع
source.dir = .

# (str) نام فایل اصلی
source.main = main.py

# (str) نسخه برنامه
version = 1.0

# (list) فایل‌های منبع برای شامل شدن
source.include_exts = py,png,jpg,kv,atlas

# (list) نیازمندی‌های برنامه
requirements = python3,kivy

# (str) جهت‌گیری پشتیبانی‌شده
orientation = portrait

# تنظیمات خاص اندروید
# (int) API هدف اندروید
android.api = 33

# (int) حداقل API
android.minapi = 21

# (str) نسخه NDK اندروید
android.ndk = 23b

# (str) مسیر SDK اندروید
android.sdk_path = /home/runner/android-sdk

# (str) مسیر NDK اندروید
android.ndk_path = /home/runner/android-ndk-r23b

# (bool) پذیرش خودکار مجوزهای SDK
android.accept_sdk_license = True

[buildozer]
# (int) سطح لاگ (ස

System: برای رفع خطای گزارش‌شده، باید اطمینان حاصل کنیم که فایل `buildozer.spec` با قالب درست (LF) ذخیره شده و فایل‌های منبع به درستی در دسترس هستند. از آنجا که فایل `main.py` در ریشه پروژه وجود دارد، مشکل اصلی به احتمال زیاد به دلیل وجود کاراکترهای CRLF در فایل `buildozer.spec` است. در ادامه، مراحل دقیق برای رفع این مشکل ارائه شده است.

### مراحل اعمال راه‌حل

#### ۱. اصلاح فایل `buildozer.spec`
1. **باز کردن فایل در ویرایشگر مناسب**:
   - فایل `buildozer.spec` را در یک ویرایشگر متن مانند **VS Code** یا **Notepad++** باز کنید.
   - مطمئن شوید که فایل با قالب **LF** (Unix-style line endings) ذخیره شده است:
     - در **VS Code**: در پایین صفحه، نوع پایان خط (Line Ending) را از CRLF به LF تغییر دهید و فایل را ذخیره کنید.
     - در **Notepad++**: به منوی **Edit > EOL Conversion > Unix (LF)** بروید و فایل را ذخیره کنید.
     - در محیط لینوکس/مک، می‌توانید از دستور زیر برای تبدیل CRLF به LF استفاده کنید:
       ```bash
       sed -i 's/\r$//' buildozer.spec
