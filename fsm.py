from transitions.extensions import GraphMachine

from utils import send_text_message, send_carousel_message
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests



class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    # is_going_to_
    def is_going_to_main_table(self, event):
        text = event.message.text
        send_text_message(event.reply_token, text.lower())
        return text.lower() == "main_table"

    def is_going_to_ptt(self, event):
        text = event.message.text
        return text.lower() == "ppt"

    def is_going_to_pttbox(self, event):
        text = event.message.text
        return text.lower() == "pptbox"

    def is_going_to_pttlive(self, event):
        text = event.message.text
        return text.lower() == "pptlive"

    def is_going_to_ptthot(self, event):
        text = event.message.text
        return text.lower() == "ppthot"

    def is_going_to_highlights(self, event):
        text = event.message.text
        return text.lower() == "highlights"

    def is_going_to_yt_search(self, event):
        text = event.message.text
        return text.lower() == "yt_search"

    def is_going_to_yt_output(self, event):
        text = event.message.text
        return text.lower() == "yt_output"

    def is_going_to_choose_team(self, event):
        text = event.message.text
        return text.lower() == "choose_team"

    def is_going_to_show_team_record(self, event):
        text = event.message.text
        return text.lower() == "show_team_record"

    def is_going_to_search_player(self, event):
        text = event.message.text
        return text.lower() == "search_player"

    def is_going_to_show_player_stats(self, event):
        text = event.message.text
        return text.lower() == "show_player_stats"

    def is_going_to_data(self, event):
        text = event.message.text
        return text.lower() == "data"

    def is_going_to_show_stats_leader(self, event):
        text = event.message.text
        return text.lower() == "show_stats_leader"


    # main_table
    def on_enter_main_table(self, event):
        reply_token = event.reply_token

        img_url = []
        img_url.append('https://imgur.com/a/XGkj1te') # ptt nba
        img_url.append('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ03k-NhlEgFbCMQD9xvKO5oiJSnW4ldzp49w&usqp=CAU') # nba highlights
        img_url.append('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRzdKpTVlJhlqcnnUPpS3vNych2o27NDcBlA&usqp=CAU') # nba stats

        label_list = []
        label_list.append('PTT')
        label_list.append('Highlights')
        label_list.append('Stats Leaders')

        text_list = []
        text_list.append('ptt')
        text_list.append('highlights')
        text_list.append('data')
        

        column = []
        for i in range(3):
            x = ImageCarouselColumn(
                image_url=img_url[i],
                action=MessageTemplateAction(
                    label=label_list[i],
                    text=text_list[i]
                )
            )
            column.append(x)

        send_carousel_message(reply_token, column)


    # ptt
    def on_enter_ptt(self, event):
        reply_token = event.reply_token

        img_url = []
        img_url.append('https://imgur.com/a/J9zgMNY') # box
        img_url.append('https://imgur.com/a/XPpGEcb') # live
        img_url.append('https://imgur.com/a/hOkGtCZ') # 爆

        label_list = []
        label_list.append('Box')
        label_list.append('Live')
        label_list.append('爆文')

        text_list = []
        text_list.append('pttbox')
        text_list.append('pttlive')
        text_list.append('ptthot')

        column = []
        for i in range(3):
            x = ImageCarouselColumn(
                image_url=img_url[i],
                action=MessageTemplateAction(
                    label=label_list[i],
                    text=text_list[i]
                )
            )
            column.append(x)

        send_carousel_message(reply_token, column)


    # pttbox
    def on_enter_pttbox(self, event):
        reply_token = event.reply_token

        title_list_td = []
        title_list_ystrd = []
        url_list_td = []
        url_list_ystrd = []
        date_list_td = []
        date_list_ystrd = []
        ptt_url = 'https://www.ptt.cc'

        today = datetime.now()
        year_td = today.year
        yesterday = today-timedelta(1)
        year_ystrd = yesterday.year
        today = str(today.month)+'/'+str(today.day)
        yesterday = str(yesterday.month)+'/'+str(yesterday.day)

        title_url = ''
        title_text = ''
        url = 'https://www.ptt.cc/bbs/NBA/index.html' # ptt basketball
        count = 0
        while True:
            break_or_not = False

            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            ini_resault = soup.select('.r-ent')

            for tmp_resault in ini_resault:
                tmp = tmp_resault.select('div.date')
                title_tmp = tmp_resault.select('.title a')

                for i in title_tmp:
                    title_url = ptt_url+i['href']
                    title_text = i.text

                for i in tmp:
                    if i.text==today:
                        date_list_td.append(i.text)
                        title_list_td.append(title_text)
                        url_list_td.append(title_url)
                    elif i.text==yesterday:
                        date_list_ystrd.append(i.text)
                        title_list_ystrd.append(title_text)
                        url_list_ystrd.append(title_url)
                    else:
                        break_or_not = True

            gate = 0
            new_url = ''
            for_url = soup.select('.btn.wide')
            for i in for_url:
                for j in i:
                    if j=='‹ 上頁':
                        new_url = ptt_url+i['href']
                        gate = 1
                        break
                if gate==1:
                    break
            
            if count == 0: # 最少爬兩頁
                url = new_url
                count+=1
            else:
                if break_or_not:
                    break
                else:
                    url = new_url
                    count+=1
            
        final_url_td = []
        final_title_td = []
        final_url_ystrd = []
        final_title_ystrd = []
        for i in range(len(url_list_td)):
            if title_list_td[i].find('[BOX ]')==0:
                final_url_td.append(url_list_td[i])
                final_title_td.append(title_list_td[i])
        for i in range(len(url_list_ystrd)):
            if title_list_ystrd[i].find('[BOX ]')==0:
                final_url_ystrd.append(url_list_ystrd[i])
                final_title_ystrd.append(title_list_ystrd[i])

        # combine text
        text_td = ''
        for i in range(len(final_url_td)):
            text_td += final_title_td[i]+'\n'+final_url_td[i]+'\n\n'
        if text_td=='':
            text_td = 'None'

        text_ystrd = ''
        for i in range(len(final_url_ystrd)):
            text_ystrd += final_title_ystrd[i]+'\n'+final_url_ystrd[i]+'\n\n'
        if text_ystrd=='':
            text_ystrd = 'None'

        text_td = str(year_td)+'/'+today+'\n\n'+text_td
        text_ystrd = str(year_ystrd)+'/'+yesterday+'\n\n'+text_ystrd

        send_text_message(reply_token, text_td)
        send_text_message(reply_token, text_ystrd)
