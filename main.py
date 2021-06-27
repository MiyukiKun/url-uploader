from telethon import events
from config import bot
import downloader
import os
from FastTelethon import upload_file
import time

is_busy = False


class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False


@bot.on(events.NewMessage(pattern=("/start")))
async def start(event):
    await bot.send_message(event.chat_id, "Im Running")


@bot.on(events.NewMessage(pattern=("/upload")))
async def download_function(event):
    global is_busy
    if is_busy == True:
        await event.reply("Im busy with a diffrent task right now, try again later")
        return
    is_busy = True
    try:
        try:
            x = await event.get_reply_message()
            thumb = await bot.download_media(x.photo)
            print(thumb)
        except:
            thumb = "thumb.png"

        split = event.raw_text[8:]
        reply = await event.reply("Downloading")
        for_name = split.split("|")
        url = for_name[0]
        url = url.replace(' ', '')
        try:
            name = for_name[1]
        except:
            name = url.split("/")[-1]
        await downloader.DownLoadFile(url, 1024*10, reply, file_name=name)
        await Upload(event, reply, name, thumb)
        await reply.delete()
        os.remove(name)

    except Exception as e:
        await reply.edit(str(e))

    finally:
        is_busy = False


async def Upload(event, reply, out, thumbnail):
    timer = Timer()

    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            await reply.edit(f"Uploading... {human_readable_size(downloaded_bytes)}/{human_readable_size(total_bytes)}")

    with open(out, "rb") as f:
        ok = await upload_file(
            client=bot,
            file=f,
            name=out,
            progress_callback=progress_bar
        )
    await bot.send_message(
        event.chat_id, file=ok,
        force_document=True,
        thumb=thumbnail
    )


def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


@bot.on(events.NewMessage(pattern=("/batch")))
async def batch(event):
    global is_busy
    if is_busy == True:
        await event.reply("Im busy with a diffrent task right now, try again later")
        return
    is_busy = True

    try:
        x = await event.get_reply_message()
        msg = x.raw_text.split("\n\n")
        thumb = await bot.download_media(x.photo)
        if thumb == None:
            thumb = "thumb.png"

        for i in msg:
            reply = await event.reply(f"Downloading")
            for_name = i.split("|")
            url = for_name[0]
            url = url.replace(' ', '')
            try:
                name = for_name[1]
            except:
                name = url.split("/")[-1]
            await downloader.DownLoadFile(url, 1024*10, reply, file_name=name)
            await Upload(event, reply, name, thumb)
            os.remove(name)
            await reply.delete()

    except Exception as e:
        await event.reply(e)

    finally:
        is_busy = False


@bot.on(events.NewMessage(pattern=("/setthumb")))
async def thumb(event):
    x = await event.get_reply_message()
    thumb = await bot.download_media(x.photo)
    with open(thumb, "rb") as f:
        pic = f.read()
    with open("thumb.png", "wb") as f:
        f.write(pic)
    await event.reply("Set as default thumbnail")


@bot.on(events.NewMessage(pattern=("/clearthumb")))
async def clear_thumb(event):
    with open("thumb.png", "w") as f:
        f.write("")
    await event.reply("cleared thumbnail")


@bot.on(events.NewMessage(pattern=("/status")))
async def status(event):
    await event.reply(f"{is_busy = }")


@bot.on(events.NewMessage(pattern=("/viewthumb")))
async def view(event):
    try:
        await event.reply("current default thumbnail", file="thumb.png")
    except:
        await event.reply("No default thumbnail set")


bot.start()

bot.run_until_disconnected()
