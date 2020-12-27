from transitions.extensions import GraphMachine

from utils import send_text_message, send_carousel_message
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import requests



class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    # is_going_to_
    # def is_going_to_main_table(self, event):
    #     text = event.message.text
    #     print('is_going_to_main_table')
    #     return True

    def is_going_to_ptt(self, event):
        text = event.message.text
        
        return text.lower() == "ptt"

    def is_going_to_pttbox(self, event):
        text = event.message.text
        return text.lower() == "pttbox"

    def is_going_to_pttlive(self, event):
        text = event.message.text
        return text.lower() == "pttlive"

    def is_going_to_ptthot(self, event):
        text = event.message.text
        return text.lower() == "ptthot"


    # main_table
    def on_enter_main_table(self, event):
        print('on_enter_main_table')
        reply_token = event.reply_token

        img_url = []
        img_url.append('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTi5ehTVtlI33F7CaydVwWwtE8nmn5XLa5zew&usqp=CAU') # ptt nba

        label_list = []
        label_list.append('PTT')

        text_list = []
        text_list.append('ptt')

        column = []
        x = ImageCarouselColumn(
            image_url=img_url[0],
            action=MessageTemplateAction(
                label=label_list[0],
                text=text_list[0]
            )
        )
        column.append(x)

        send_carousel_message(reply_token, column)


    # ptt
    def on_enter_ptt(self, event):
        reply_token = event.reply_token

        img_url = []
        img_url.append('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6-GyU9jA6AITXvjPe1I4kwQf-YeB6ZUQacg&usqp=CAU') # box
        img_url.append('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSzR5Tfb0LWTSDrv-D3Skfr7nAlXs6FoLv2-g&usqp=CAU') # live
        img_url.append('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQK_kX1uH62OowBxlIXDc7ywTs29RowKXPzBQ&usqp=CAU') # 爆

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
        self.for_ptt_BOX_and_Live(event, '[BOX ]')
        

    # pttlive
    def on_enter_pttlive(self, event):
        self.for_ptt_BOX_and_Live(event, '[Live]')
       

    def for_ptt_BOX_and_Live(self, event, target: str):
        reply_token = event.reply_token

        title_list_td = []
        title_list_ystrd = []
        url_list_td = []
        url_list_ystrd = []
        date_list_td = []
        date_list_ystrd = []
        ptt_url = 'https://www.ptt.cc'

        today = datetime.now().astimezone(timezone(timedelta(hours=8))) # 轉換時區：東8
        year_td = today.year
        yesterday = today-timedelta(1)
        year_ystrd = yesterday.year
        today = str(today.month)+'/'+str(today.day)
        yesterday = str(yesterday.month)+'/'+str(yesterday.day)

        title_url = ''
        title_text = ''
        url = 'https://www.ptt.cc/bbs/NBA/index.html' # ptt nba
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
            if title_list_td[i].find(target)==0:
                final_url_td.append(url_list_td[i])
                final_title_td.append(title_list_td[i])
        for i in range(len(url_list_ystrd)):
            if title_list_ystrd[i].find(target)==0:
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

        send_text_message(reply_token, text_td+'\n\n\n'+text_ystrd)


    # ptthot
    def on_enter_ptthot(self, event):
        reply_token = event.reply_token

        qualified_date = []
        qualified_year = []
        today = datetime.now().astimezone(timezone(timedelta(hours=8))) # 轉換時區：東8
        for i in range(7):
            date = today-timedelta(i)
            qualified_date.append(str(date.month)+'/'+str(date.day))
            qualified_year.append(str(date.year))

        title_list = []
        url_list = []
        date_list = []
        
        pushNum = ''
        title_url = ''
        title_text = ''

        ptt_url = 'https://www.ptt.cc'
        url = 'https://www.ptt.cc/bbs/NBA/index.html' # ptt nba

        count = 0
        while True:
            break_or_not = False

            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            ini_resault = soup.select('.r-ent')

            tmp_title_list = []
            tmp_url_list = []
            tmp_date_list = []
            for tmp_resault in ini_resault:
                pushNum = ''

                tmp_pushNum = tmp_resault.select('.hl.f1') # find the number of push
                for i in tmp_pushNum:
                    pushNum = i.text

                if pushNum=='爆':
                    tmp = tmp_resault.select('div.date') # find the date
                    for i in tmp:
                        key = False
                        for j in range(len(qualified_date)):
                            if i.text==qualified_date[j]:
                                title_tmp = tmp_resault.select('.title a') # find the information of title (url & text)
                                for k in title_tmp:
                                    title_url = ptt_url+k['href']
                                    title_text = k.text

                                tmp_date_list.append(qualified_year[j]+'/'+qualified_date[j])
                                tmp_title_list.append(title_text)
                                tmp_url_list.append(title_url)

                                key = True
                                break
                        
                        if key==False:
                            break_or_not = True


            # get a new url of '上頁'
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
            
            # 至少爬兩頁，避開置底公告的影響
            if count == 0:
                url = new_url
                count+=1
            else:
                if break_or_not:
                    break
                else:
                    url = new_url
                    count+=1

            # reverse these temporary lists
            tmp_date_list.reverse()
            tmp_title_list.reverse()
            tmp_url_list.reverse()

            # list.append(tmp_list_reversed)
            for i in range(len(tmp_title_list)):
                date_list.append(tmp_date_list[i])
                title_list.append(tmp_title_list[i])
                url_list.append(tmp_url_list[i])
            

        # combine text
        text_ = '最近一個禮拜的爆文如下：\n\n'
        for i in range(len(title_list)):
            text_ += '('+date_list[i]+')'+'\n'+title_list[i]+'\n'+url_list[i]+'\n\n'

        send_text_message(reply_token, text_)

