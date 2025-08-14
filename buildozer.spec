[app]
title = Tile Match Explorer
package.name = tileexplorer
package.domain = org.yourname
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,webp,ogg,wav,mp3,ttf,json
version = 0.1.0
orientation = landscape
fullscreen = 0
presplash.filename = 
icon.filename = 

requirements = python3,kivy
# If you later need KivyMD or others, add them here (comma-separated).

# If you rely on SDL2 mixer alternatives, keep default. Kivy SoundLoader handles wav/ogg/mp3 depending on device codecs.

[buildozer]
log_level = 2
warn_on_root = 0
