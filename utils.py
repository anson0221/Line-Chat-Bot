import os

from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, ImageCarouselTemplate, ImageSendMessage


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"

def send_carousel_message(reply_token, column_):
    line_bot_api = LineBotApi(channel_access_token)
    print(column_)
    message = TemplateSendMessage(
        alt_text='Carousel Template', 
        template=ImageCarouselTemplate(columns=column_)
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_image_message(reply_token, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"
