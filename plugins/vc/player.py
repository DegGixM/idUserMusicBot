"""Telegram Sesli Sohbette Ses çalma ve Kontrol Etme

bağımlılıklar:
- ffmpeg

Gerekli grup yöneticisi izinleri:
- Mesajları sil
- Sesli sohbetleri yönetin (isteğe bağlı)

Nasıl kullanılır:
- userbot'u başlatın
- sesli sohbet etkinleştirilmiş bir grup sohbetine !join gönder
   userbot hesabının kendisinden veya bağlantılarından
- çalmaya başlamak için /play ile bir sesi yanıtlayın
   sesli sohbette, grubun her üyesi
   şimdi !play komutunu kullanabilir
- daha fazla komut için !help'i kontrol edin
"""
import os
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters, emoji
from pyrogram.types import Message
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pytgcalls import GroupCall
import ffmpeg

DELETE_DELAY = 8

USERBOT_HELP = f"""{emoji.LABEL}  **Ortak Komutlar**:
__mevcut sesli sohbetin grup üyeleri tarafından kullanılabilir__
__/(eğik çizgi) veya ! ile başlar (ünlem işareti)__

/play sıraya almak veya çalma listesini göstermek için bir sesle yanıtlayın
/current  geçerli parçanın geçerli oynatma süresini göster
/repo userbot'un github deposunu göster
`!help` komutlar için yardım göster

{emoji.LABEL}  **Yönetici Komutları**:
__userbot hesabının kendisi ve kişileri tarafından kullanılabilir__
__ile başlar ! (ünlem işareti)__

✯ `!skip` çalmakta olan şarkıyı atla,
✯ `!join` mevcut grubun sesli sohbetine katılın,
✯ `!leave` mevcut sesli sohbetten çık,
✯ `!vc` hangi VC'nin birleştirildiğini kontrol edin,
✯ `!stop` oynamayı bırak,
✯ `!replay` baştan oynat,
✯ `!clean` kullanılmayan RAW PCM dosyalarını kaldırır,
✯ `!pause` oynatmayı duraklatın,
✯ `!resume` oynamaya devam edin,
✯ `!mute` VC kullanıcı robotunu sessize alır,
✯ `!unmute` VC kullanıcı robotunun sesini açar.

✯ Tarafından Sağlanan 🤖 **[DejavuGurup](https://t.me/DejavuGurup)**
✯ Destek Için 🆘 **[DejavuSupport](https://t.me/DejavuSupport)**"""

USERBOT_REPO = f"""{emoji.ROBOT} Tamil Voice Chat UserBot
» Depo: **[GitHub](https://github.com/DegGixM/idUserMusicBot)**
» Destek Için:**[DejavuSupport](https://t.me/DejavuSupport)**
» License: AGPL-3.0-or-later"""


# - Pyrogram filters

main_filter = (
    filters.group
    & filters.text
    & ~filters.edited
    & ~filters.via_bot
)
self_or_contact_filter = filters.create(
    lambda
    _,
    __,
    message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)


async def current_vc_filter(_, __, m: Message):
    group_call = mp.group_call
    if not group_call.is_connected:
        return False
    chat_id = int("-100" + str(group_call.full_chat.id))
    if m.chat.id == chat_id:
        return True
    return False

current_vc = filters.create(current_vc_filter)


# - class


class MusicPlayer(object):
    def __init__(self):
        self.group_call = GroupCall(None, path_to_log_file='')
        self.chat_id = None
        self.start_time = None
        self.playlist = []
        self.msg = {}

    async def update_start_time(self, reset=False):
        self.start_time = (
            None if reset
            else datetime.utcnow().replace(microsecond=0)
        )

    async def send_playlist(self):
        playlist = self.playlist
        if not playlist:
            pl = f"{emoji.NO_ENTRY} boş çalma listesi"
        else:
            if len(playlist) == 1:
                pl = f"{emoji.REPEAT_SINGLE_BUTTON} **Calma Istesi**:\n"
            else:
                pl = f"{emoji.PLAY_BUTTON} **Calma Listesi**:\n"
            pl += "\n".join([
                f"**{i}**. **[{x.audio.title}]({x.link})**"
                for i, x in enumerate(playlist)
            ])
        if mp.msg.get('Calma Listesi') is not None:
            await mp.msg['Calma Listesi'].delete()
        mp.msg['Calma Listesi'] = await send_text(pl)


mp = MusicPlayer()


# - pytgcalls handlers


@mp.group_call.on_network_status_changed
async def network_status_changed_handler(gc: GroupCall, is_connected: bool):
    if is_connected:
        mp.chat_id = int("-100" + str(gc.full_chat.id))
        await send_text(f"{emoji.CHECK_MARK_BUTTON} Sesli Sohbete Katıldı")
    else:
        await send_text(f"{emoji.CROSS_MARK_BUTTON} Sesli Sohbetten Ayrıldı")
        mp.chat_id = None


@mp.group_call.on_playout_ended
async def playout_ended_handler(group_call, filename):
    await skip_current_playing()


# - Pyrogram handlers


@Client.on_message(
    filters.group
    & ~filters.edited
    & current_vc
    & (filters.regex("^(\\/|!)play$") | filters.audio)
)
async def play_track(client, m: Message):
    group_call = mp.group_call
    playlist = mp.playlist
    # check audio
    if m.audio:
        if m.audio.duration > 600:
            reply = await m.reply_text(
                f"{emoji.ROBOT} 10 dakikadan uzun süren ses "
                 "oynatma listesine otomatik olarak eklenmez"
            )
            await _delay_delete_messages((reply, ), DELETE_DELAY)
            return
        m_audio = m
    elif m.reply_to_message and m.reply_to_message.audio:
        m_audio = m.reply_to_message
    else:
        await mp.send_playlist()
        await m.delete()
        return
    # check already added
    if playlist and playlist[-1].audio.file_unique_id \
            == m_audio.audio.file_unique_id:
        reply = await m.reply_text(f"{emoji.ROBOT} Çoktan eklenmiş")
        await _delay_delete_messages((reply, m), DELETE_DELAY)
        return
    # add to playlist
    playlist.append(m_audio)
    if len(playlist) == 1:
        m_status = await m.reply_text(
            f"{emoji.INBOX_TRAY} Indirme ve Kod Dönüştürme..."
        )
        await download_audio(playlist[0])
        group_call.input_filename = os.path.join(
            client.workdir,
            DEFAULT_DOWNLOAD_DIR,
            f"{playlist[0].audio.file_unique_id}.raw"
        )
        await mp.update_start_time()
        await m_status.delete()
        print(f"- OYUNA BAŞLA: {playlist[0].audio.title}")
    await mp.send_playlist()
    for track in playlist[:2]:
        await download_audio(track)
    if not m.audio:
        await m.delete()


@Client.on_message(main_filter
                   & current_vc
                   & filters.regex("^(\\/|!)current$"))
async def show_current_playing_time(client, m: Message):
    start_time = mp.start_time
    playlist = mp.playlist
    if not start_time:
        reply = await m.reply_text(f"{emoji.PLAY_BUTTON} current")
        await _delay_delete_messages((reply, m), DELETE_DELAY)
        return
    utcnow = datetime.utcnow().replace(microsecond=0)
    if mp.msg.get('current') is not None:
        await mp.msg['current'].delete()
    mp.msg['current'] = await playlist[0].reply_text(
        f"{emoji.PLAY_BUTTON}  {utcnow - start_time} / "
        f"{timedelta(seconds=playlist[0].audio.duration)}",
        disable_notification=True
    )
    await m.delete()


@Client.on_message(main_filter
                   & (self_or_contact_filter | current_vc)
                   & filters.regex("^(\\/|!)help$"))
async def show_help(client, m: Message):
    if mp.msg.get('help') is not None:
        await mp.msg['help'].delete()
    mp.msg['help'] = await m.reply_text(
         USERBOT_HELP, 
         disable_web_page_preview=True,
         quote=False

    )
    await m.delete()


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.command("skip", prefixes="!"))
async def skip_track(client, m: Message):
    playlist = mp.playlist
    if len(m.command) == 1:
        await skip_current_playing()
    else:
        try:
            items = list(dict.fromkeys(m.command[1:]))
            items = [int(x) for x in items if x.isdigit()]
            items.sort(reverse=True)
            text = []
            for i in items:
                if 2 <= i <= (len(playlist) - 1):
                    audio = f"[{playlist[i].audio.title}]({playlist[i].link})"
                    playlist.pop(i)
                    text.append(f"{emoji.WASTEBASKET} {i}. **{audio}**")
                else:
                    text.append(f"{emoji.CROSS_MARK} {i}")
            reply = await m.reply_text("\n".join(text))
            await mp.send_playlist()
        except (ValueError, TypeError):
            reply = await m.reply_text(f"{emoji.NO_ENTRY} invalid input",
                                       disable_web_page_preview=True)
        await _delay_delete_messages((reply, m), DELETE_DELAY)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & filters.regex("^!join$"))
async def join_group_call(client, m: Message):
    group_call = mp.group_call
    group_call.client = client
    if group_call.is_connected:
        await m.reply_text(f"{emoji.ROBOT} already joined a voice chat")
        return
    await group_call.start(m.chat.id)
    await m.delete()


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!leave$"))
async def leave_voice_chat(client, m: Message):
    group_call = mp.group_call
    mp.playlist.clear()
    group_call.input_filename = ''
    await group_call.stop()
    await m.delete()


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & filters.regex("^!vc$"))
async def list_voice_chat(client, m: Message):
    group_call = mp.group_call
    if group_call.is_connected:
        chat_id = int("-100" + str(group_call.full_chat.id))
        chat = await client.get_chat(chat_id)
        reply = await m.reply_text(
            f"{emoji.MUSICAL_NOTES} **currently in the voice chat**:\n"
            f"- **{chat.title}**"
        )
    else:
        reply = await m.reply_text(emoji.NO_ENTRY
                                   + "didn't join any voice chat yet")
    await _delay_delete_messages((reply, m), DELETE_DELAY)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!stop$"))
async def stop_playing(_, m: Message):
    group_call = mp.group_call
    group_call.stop_playout()
    reply = await m.reply_text(f"{emoji.STOP_BUTTON} stopped playing")
    await mp.update_start_time(reset=True)
    mp.playlist.clear()
    await _delay_delete_messages((reply, m), DELETE_DELAY)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!replay$"))
async def restart_playing(_, m: Message):
    group_call = mp.group_call
    if not mp.playlist:
        return
    group_call.restart_playout()
    await mp.update_start_time()
    reply = await m.reply_text(
        f"{emoji.COUNTERCLOCKWISE_ARROWS_BUTTON}  "
        "playing from the beginning..."
    )
    await _delay_delete_messages((reply, m), DELETE_DELAY)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!pause"))
async def pause_playing(_, m: Message):
    mp.group_call.pause_playout()
    await mp.update_start_time(reset=True)
    reply = await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} paused",
                               quote=False)
    mp.msg['pause'] = reply
    await m.delete()


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!resume"))
async def resume_playing(_, m: Message):
    mp.group_call.resume_playout()
    reply = await m.reply_text(f"{emoji.PLAY_OR_PAUSE_BUTTON} resumed",
                               quote=False)
    if mp.msg.get('pause') is not None:
        await mp.msg['pause'].delete()
    await m.delete()
    await _delay_delete_messages((reply, ), DELETE_DELAY)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!clean$"))
async def clean_raw_pcm(client, m: Message):
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    all_fn = os.listdir(download_dir)
    for track in mp.playlist[:2]:
        track_fn = f"{track.audio.file_unique_id}.raw"
        if track_fn in all_fn:
            all_fn.remove(track_fn)
    count = 0
    if all_fn:
        for fn in all_fn:
            if fn.endswith(".raw"):
                count += 1
                os.remove(os.path.join(download_dir, fn))
    reply = await m.reply_text(f"{emoji.WASTEBASKET} cleaned {count} files")
    await _delay_delete_messages((reply, m), DELETE_DELAY)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!mute$"))
async def mute(_, m: Message):
    group_call = mp.group_call
    group_call.set_is_mute(True)
    reply = await m.reply_text(f"{emoji.MUTED_SPEAKER} muted")
    await _delay_delete_messages((reply, m), DELETE_DELAY)


@Client.on_message(main_filter
                   & self_or_contact_filter
                   & current_vc
                   & filters.regex("^!unmute$"))
async def unmute(_, m: Message):
    group_call = mp.group_call
    group_call.set_is_mute(False)
    reply = await m.reply_text(f"{emoji.SPEAKER_MEDIUM_VOLUME} unmuted")
    await _delay_delete_messages((reply, m), DELETE_DELAY)


@Client.on_message(main_filter
                   & current_vc
                   & filters.regex("^(\\/|!)repo$"))
async def show_repository(_, m: Message):
    if mp.msg.get('repo') is not None:
        await mp.msg['repo'].delete()
    mp.msg['repo'] = await m.reply_text(
        USERBOT_REPO,
        disable_web_page_preview=True,
        quote=False
    )
    await m.delete()


# - Other functions


async def send_text(text):
    group_call = mp.group_call
    client = group_call.client
    chat_id = mp.chat_id
    message = await client.send_message(
        chat_id,
        text,
        disable_web_page_preview=True,
        disable_notification=True
    )
    return message


async def skip_current_playing():
    group_call = mp.group_call
    playlist = mp.playlist
    if not playlist:
        return
    if len(playlist) == 1:
        await mp.update_start_time()
        return
    client = group_call.client
    download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
    group_call.input_filename = os.path.join(
        download_dir,
        f"{playlist[1].audio.file_unique_id}.raw"
    )
    await mp.update_start_time()
    # remove old track from playlist
    old_track = playlist.pop(0)
    print(f"- START PLAYING: {playlist[0].audio.title}")
    await mp.send_playlist()
    os.remove(os.path.join(
        download_dir,
        f"{old_track.audio.file_unique_id}.raw")
    )
    if len(playlist) == 1:
        return
    await download_audio(playlist[1])


async def download_audio(m: Message):
    group_call = mp.group_call
    client = group_call.client
    raw_file = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR,
                            f"{m.audio.file_unique_id}.raw")
    if not os.path.isfile(raw_file):
        original_file = await m.download()
        ffmpeg.input(original_file).output(
            raw_file,
            format='s16le',
            acodec='pcm_s16le',
            ac=2,
            ar='48k',
            loglevel='error'
        ).overwrite_output().run()
        os.remove(original_file)


async def _delay_delete_messages(messages: tuple, delay: int):
    await asyncio.sleep(delay)
    for m in messages:
        await m.delete()
