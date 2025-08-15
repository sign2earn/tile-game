[app]
# (str) عنوان برنامه
title = Tile Match Explorer

# (str) نام بسته
package.name = tileexplorer

# (str) دامنه بسته
package.domain = org.yourname

# (str) مسیر پوشه منبع
source.dir = .

# (str) نام فایل اصلی
source.main = main.py

# (str) نسخه برنامه
version = 0.1.0

# (list) فایل‌های منبع برای شامل شدن
source.include_exts = py,kv,png,jpg,jpeg,webp,ogg,wav,mp3,ttf,json

# (str) جهت‌گیری پشتیبانی‌شده
orientation = landscape

# (int) تمام‌صفحه
fullscreen = 0

# (str) فایل پیش‌بارگذاری (اختیاری)
presplash.filename =

# (str) فایل آیکون (اختیاری)
icon.filename =

# (list) نیازمندی‌های برنامه
requirements = python3,kivy

# تنظیمات خاص اندروید
# (int) API هدف اندروید
android.api = 33

# (int) حداقل API
android.minapi = 21

# (str) نسخه NDK اندروید
android.ndk = 25b

# (str) مسیر SDK اندروید
android.sdk_path = /home/runner/android-sdk

# (str) مسیر NDK اندروید
android.ndk_path = /home/runner/android-ndk-r25b

# (bool) پذیرش خودکار مجوزهای SDK
android.accept_sdk_license = True

[buildozer]
# (int) سطح لاگ (2 = دیباگ)
log_level = 2

# (int) هشدار در صورت اجرا به عنوان روت
warn_on_root = 0
