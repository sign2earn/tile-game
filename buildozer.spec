[app]
# (str) عنوان برنامه
title = TileExplorer

# (str) نام بسته
package.name = tileexplorer

# (str) دامنه بسته
package.domain = org.tileexplorer

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
# (int) سطح لاگ (2 = دیباگ)
log_level = 2

# (int) هشدار در صورت اجرا به عنوان روت
warn_on_root = 1