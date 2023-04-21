import telegram
import requests
import m3u8
import datetime
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


# Replace YOUR_TOKEN with your bot token
TOKEN = '5900582242:AAFfxB2iwSxVp9FyksYdi0NeLV2WoQq1ihg'
bot = telegram.Bot(token=TOKEN)


def start(update, context):
    update.message.reply_text('Please send me the URL of the video you want to download and the corresponding quality number')


def handle_input(update, context):
    # Parse the input message and extract the URL and quality
    text = update.message.text.split()
    if len(text) != 2:
        update.message.reply_text('Invalid input. Please send the URL of the video and the corresponding quality number.')
        return
    url, quality_index_str = text

    # Check if the quality index is valid
    try:
        quality_index = int(quality_index_str)
    except ValueError:
        update.message.reply_text('Invalid quality index. Please enter a valid integer.')
        return

    # Download the video file from the selected quality stream
    r = requests.get(url)
    m3u8_master = m3u8.loads(r.text)
    try:
        update.message.reply_text('Downloading...')
        pl_url = m3u8_master.data['playlists'][quality_index]['uri']
    except IndexError:
        update.message.reply_text('Invalid quality index. Please choose a number between 0 and {}.'.format(len(m3u8_master.data['playlists'])-1))
        return

    r = requests.get(pl_url)
    playlist = m3u8.loads(r.text)

    # Generate a timestamp for the video file
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = timestamp + '.ts'

    with open(filename, "wb") as f:
        for segment in playlist.data['segments']:
            url = segment['uri']
            r = requests.get(url)
            f.write(r.content)

    with open(filename, 'rb') as f:
        update.message.reply_video(video=f, supports_streaming=True,timeout=600)
        update.message.reply_text('Downloaded!')

    # Delete the downloaded file
    os.remove(filename)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_input))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
