[app]
title = VG Admin
package.name = vgadmin
package.domain = org.vegetablegarden
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,qrcode,requests,urllib3,chardet,idna,openssl

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk_api = 25b
p4a.branch = master

[buildozer]
log_level = 2

warn_on_root = 1
