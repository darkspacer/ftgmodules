# requires: pySmartDL
# requires: hachoir
# requires: datetime
# requires: zipfile
# requires: patool

import asyncio
import os
import time
import zipfile
import patool
import subprocess
from telethon import events
from pySmartDL import SmartDL
from uniborg.util import admin_cmd, humanbytes, progress, time_formatter
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from zipfile import ZipFile
from datetime import datetime
from sample_config import Config



extracted = Config.TMP_DOWNLOAD_DIRECTORY + "извлечено/"
thumb_image_path = Config.TMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"
if not os.path.isdir(extracted):
    os.makedirs(extracted)


@borg.on(admin_cmd(pattern="unzip"))
async def _(event):
    if event.fwd_from:
        return
    mone = await event.edit("В процессе")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await borg.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "пытаюсь загрузить")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Заархивировано в `{}` в течении {} секунд by @aivengog.".format(downloaded_file_name, ms))

        with zipfile.ZipFile(downloaded_file_name, 'r') as zip_ref:
            zip_ref.extractall(extracted)
        filename = sorted(get_lst_of_files(extracted, []))
        #filename = filename + "/"
        await event.edit("Вскрываю архив")
        # r=root, d=directories, f = files
        for single_file in filename:
            if os.path.exists(single_file):
                # https://stackoverflow.com/a/678242/4723940
                caption_rts = os.path.basename(single_file)
                force_document = True
                supports_streaming = False
                document_attributes = []
                if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
                    metadata = extractMetadata(createParser(single_file))
                    duration = 0
                    width = 0
                    height = 0
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds
                    if os.path.exists(thumb_image_path):
                        metadata = extractMetadata(createParser(thumb_image_path))
                        if metadata.has("width"):
                            width = metadata.get("width")
                        if metadata.has("height"):
                            height = metadata.get("height")
                    document_attributes = [
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True
                        )
                    ]
                try:
                    await borg.send_file(
                        event.chat_id,
                        single_file,
                        caption=f"Извлёк `{caption_rts}` by @aivengog",
                        force_document=force_document,
                        supports_streaming=supports_streaming,
                        allow_cache=False,
                        reply_to=event.message.id,
                        attributes=document_attributes,
                        # progress_callback=lambda d, t: asyncio.get_event_loop().create_task(  не обращайте внимания
                        #     progress(d, t, event, c_time, "пытаюсь загрузить") не обращайте внимания
                        # )
                    )
                except Exception as e:
                    await borg.send_message(
                        event.chat_id,
                        "{} вызвано `{}`".format(caption_rts, str(e)),
                        reply_to=event.message.id
                    )
                    # с некоторыми медиа проблемка
                    continue
                os.remove(single_file)
        os.remove(downloaded_file_name)

def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst
    
    
    
    


@borg.on(admin_cmd("zip"))
async def _(event):
    if event.fwd_from:
        return
    if not event.is_reply:
        await event.edit("Ответьте на файл, чтобы сжать его.")
        return
    mone = await event.edit("`В процессе`")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await borg.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "пытаюсь загрузить")
                )
            )
            directory_name = downloaded_file_name
            await event.edit(downloaded_file_name)
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
    zipfile.ZipFile(directory_name + '.zip', 'w', zipfile.ZIP_DEFLATED).write(directory_name)
    await borg.send_file(
        event.chat_id,
        directory_name + ".zip",
        caption="Заархивировано by @aivengog",
        force_document=True,
        allow_cache=False,
        reply_to=event.message.id,
    )
    await event.edit("ГОТОВО!!!")
    await asyncio.sleep(7)
    await event.delete()


def zipdir(path, ziph):
    # ziph это zip handle не пугайтесь
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
            os.remove(os.path.join(root, file))
            
            
@borg.on(admin_cmd(pattern="unrar"))
async def _(event):
    if event.fwd_from:
        return
    mone = await event.edit("В процессе...")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await borg.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "пытаюсь загрузить")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Вскрыл RAR `{}` за {} секунд.".format(downloaded_file_name, ms))

        patool.extract_archive(downloaded_file_name, outdir=extracted)
        filename = sorted(get_lst_of_files(extracted, []))
        #filename = filename + "/"
        await event.edit("Сейчас вскроем")
        # r=root, d=directories, f = files
        for single_file in filename:
            if os.path.exists(single_file):
                # https://stackoverflow.com/a/678242/4723940 спасиб большое
                caption_rts = os.path.basename(single_file)
                force_document = True
                supports_streaming = False
                document_attributes = []
                if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
                    metadata = extractMetadata(createParser(single_file))
                    duration = 0
                    width = 0
                    height = 0
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds
                    if os.path.exists(thumb_image_path):
                        metadata = extractMetadata(createParser(thumb_image_path))
                        if metadata.has("width"):
                            width = metadata.get("width")
                        if metadata.has("height"):
                            height = metadata.get("height")
                    document_attributes = [
                        DocumentAttributeVideo(
                            duration=duration,
                            w=width,
                            h=height,
                            round_message=False,
                            supports_streaming=True
                        )
                    ]
                try:
                    await borg.send_file(
                        event.chat_id,
                        single_file,
                        caption=f"Вскрыл RAR `{caption_rts}`",
                        force_document=force_document,
                        supports_streaming=supports_streaming,
                        allow_cache=False,
                        reply_to=event.message.id,
                        attributes=document_attributes,
                        # progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                        #     progress(d, t, event, c_time, "trying to upload")
                        # )             не смотрите сюда!
                    )
                except Exception as e:
                    await borg.send_message(
                        event.chat_id,
                        "{} вызвано `{}`".format(caption_rts, str(e)),
                        reply_to=event.message.id
                    )
                    # это у нас были проблемы с отображением разных медиа-файлов
                    continue
                os.remove(single_file)
        os.remove(downloaded_file_name)







def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst