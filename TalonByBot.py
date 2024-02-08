import aiohttp
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
    "https://talon.by/policlinic/grodno-sdp/order/31640/36999"
]

bot = telegram.Bot(token=bot_token)



async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            global counter
            print(f"Попытка найти талон №{counter}")
            counter += 1
            await check_coupons(session)
            await asyncio.sleep(1)
        

    
async def check_coupons(session):
    for doctor_url in doctor_urls:
        async with session.get(doctor_url) as response:
            html_content = await response.text()
        soup = BeautifulSoup(html_content, "html.parser")
        calendar_div = soup.find("div", class_="calendar")
        if not calendar_div:
            continue
        
        talons_divs = calendar_div.find_all("div", class_="day_talons")

        if talons_divs:
            for talon_div in talons_divs:
                day = talon_div.find("div", class_="day")
                date = day.find("span").text.strip()
                order_talons = talon_div.find("div", class_="order_talons")
                talons = order_talons.find_all("a", class_="talon")
                for talon in talons:
                    time = talon.text.strip()
                    talon_order = soup.find("ul", id="talon_order")
                    speciality = talon_order.find("a", title="Выбор специальности").find("span").text.strip()
                    doctor_name = talon_order.find("a", title="Выбор врача").find("span").text.strip()

                    if(talon.has_attr("title") and
                           "сегодня" in talon['title'] and
                           f"{doctor_name}.{date}.{time}" not in sent_talons):
                        message = f"Доступен талон на сегодня\n{speciality}: {doctor_name}\nДата: {date}\nВремя: {time}"
                        await bot.send_message(chat_id=chat_id, text=message)
                        print(message)
                        sent_talons.add(f"{doctor_name}.{date}.{time}")
                    elif(talon.has_attr("title") and
                           "сегодня" in talon['title'] and
                           f"{doctor_name}.{date}.{time}" in sent_talons):
                        continue
                    else:
                        talon_link = talon["href"]
                        talon_link = f'<a href="https://talon.by{talon_link}">{time}</a>'
                        message = f"Доступен талон\n{speciality}: {doctor_name}\nДата: {date}\nВремя: {talon_link}"
                        if(talon_link not in sent_talons):
                            await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
                            print(message)
                            sent_talons.add(talon_link)


asyncio.run(main())
