import requests
from bs4 import BeautifulSoup
import telegram
import asyncio
from telegram.constants import ParseMode


sent_talons = set()
counter = 0

bot_token = "6981505786:AAF574i3_XhvPmpy3KgJ_eWP7GGX2Wi63qY"
chat_id = "898391631"
doctor_urls = [
    "https://talon.by/policlinic/grodno-sdp/order/8221/37060",
    "https://talon.by/policlinic/grodno-sdp/order/8221/108309",
    "https://talon.by/policlinic/grodno-sdp/order/8221/74849",
    "https://talon.by/policlinic/grodno-sdp/order/8221/84527",
    "https://talon.by/policlinic/grodno-sdp/order/31640/85039",
    "https://talon.by/policlinic/grodno-sdp/order/31640/37000",
    "https://talon.by/policlinic/grodno-sdp/order/31640/155391",
    "https://talon.by/policlinic/grodno-sdp/order/31640/51624",
    "https://talon.by/policlinic/grodno-sdp/order/31640/37053",
    "https://talon.by/policlinic/grodno-sdp/order/31640/44826",
    "https://talon.by/policlinic/grodno-sdp/order/31640/37040",
    "https://talon.by/policlinic/grodno-sdp/order/31640/37023",
    "https://talon.by/policlinic/grodno-sdp/order/31640/36999",
    "https://talon.by/policlinic/grodno-sdp/order/8220/125526"
]

# Инициализация бота
bot = telegram.Bot(token=bot_token)



async def main():
    while True:
        await check_coupons()
        await asyncio.sleep(5)
        

    
async def check_coupons():
    for doctor_url in doctor_urls:
        response = requests.get(doctor_url)
        soup = BeautifulSoup(response.content, "html.parser")
        calendar_div = soup.find("div", class_="calendar")
        if not calendar_div:
            global counter
            print(f"Попытка найти талон №{counter}")
            counter += 1
            break
        
        talons_divs = calendar_div.find_all("div", class_="day_talons")

        if talons_divs:
            for talon_div in talons_divs:
                day = talon_div.find("div", class_="day")
                date = day.find("span").text.strip()
                order_talons = talon_div.find("div", class_="order_talons")
                talons = order_talons.find_all("a", class_="talon")
                for talon in talons:
                    time = talon.text.strip()
                    talon_link = talon["href"]
                    talon_link = f'<a href="https://talon.by{talon_link}">{time}</a>'


                    talon_order = soup.find("ul", id="talon_order")
                    speciality = talon_order.find("a", title="Выбор специальности").find("span").text.strip()
                    doctor_name = talon_order.find("a", title="Выбор врача").find("span").text.strip()

        
                    message = f"Доступен талон\n{speciality}: {doctor_name}\nДата: {date}\nВремя: {talon_link}"
                    if(talon_link not in sent_talons):
                        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
                        print(message)
                        sent_talons.add(talon_link)


asyncio.run(main())
