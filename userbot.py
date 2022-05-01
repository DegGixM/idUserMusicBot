# import logging
from pyrogram import Client, idle

app = Client("tgvc")
# logging.basicConfig(level=logging.INFO)
app.start()
print('>>> USERBOTu başlatan @DejavuMusiciBot')
idle()
app.stop()
print('\n>>> USERBOT tarafından DURDURULDU @DejavuMusiciBot')

