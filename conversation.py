from collections import OrderedDict
from datetime import datetime
from telegram import chat
from telegram.ext.dispatcher import run_async
from telegram.files.inputmedia import InputMediaPhoto, InputMediaVideo
import db
import logging
import telegram
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

job_checker = None

def add_description(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    caption = db.session.query(db.Description).first() or None
    if message.photo and not message.media_group_id:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_photo(chat_id=chat_id,
                               caption=caption.text,
                               photo=message.photo[-1].file_id,
                               parse_mode=ParseMode.HTML)

    elif message.animation:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_animation(chat_id=chat_id,
                                   caption=caption.text,
                                   animation=message.animation.file_id,
                                   parse_mode=ParseMode.HTML)
    elif message.video and not message.media_group_id:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_video(chat_id=chat_id,
                               video=message.video.file_id,
                               caption=caption.text,
                               parse_mode=ParseMode.HTML)

    elif message.document:
        context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        context.bot.send_document(chat_id=chat_id,
                                  document=message.document.file_id,
                                  caption=caption.text,
                                  parse_mode=ParseMode.HTML)
    else:
        return

# @run_async
def send_album(context: CallbackContext):
    try:
        media = context.job.context['media']
        chat_id = int(context.job.context['user_id'])
        run_job = context.job.context['run_job']
        if run_job:
            messages = context.bot.send_media_group(chat_id=chat_id, media=media)
            context.bot.edit_message_caption(chat_id=chat_id, 
                                             message_id=messages.result()[-1].message_id, 
                                             caption=context.job.context['caption'],
                                             parse_mode=ParseMode.HTML)
            media.clear()
            context.job.enabled = False
            context.job.schedule_removal()
        else:
            context.job.schedule_removal()
    except Exception as e:
        print(e)

# @run_async
def process_album(update: Update, context: CallbackContext):
    message: telegram.Message = update.effective_message
    caption = db.session.query(db.Description).first() or None
    
    if message.media_group_id:
        if 'media_group_id' not in context.chat_data:  # init default data for media_group_id
            context.chat_data['media_group_id'] = message.media_group_id
        if 'media' not in context.chat_data.keys():
            context.chat_data['media'] = list()
        if 'run_job' not in context.chat_data.keys():
            context.chat_data['run_job'] = True
        
        if message.media_group_id != context.chat_data['media_group_id']:
            context.chat_data['media_group_id'] = message.media_group_id
            context.chat_data['media'].clear()
            context.chat_data['run_job'] = True

        if message.photo:
            image = InputMediaPhoto(media=message.photo[-1].file_id)
            context.chat_data['media'].append(image)
        elif message.video:
            video = InputMediaVideo(media=message.video.file_id)
            context.chat_data['media'].append(video)
        
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.message_id)

        global job_checker
        job_checker = context.job_queue.run_once(send_album, when=1, context={'user_id': update.effective_chat.id, 
                                                                'media': context.chat_data['media'],
                                                                'caption': caption.text,
                                                                'time': datetime.now(),
                                                                'run_job': context.chat_data['run_job']})
        context.chat_data['run_job'] = False
