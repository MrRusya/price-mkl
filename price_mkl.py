import os
import discord
import requests
from discord.ext import tasks
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv("api.env")
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CMC_API_KEY = os.getenv('CMC_API_KEY')  # Ключ API для CoinMarketCap

client = discord.Client(intents=discord.Intents.default())
update_interval = 60  # Оновлення кожну 1 хвилину (60 секунд)

# Змінна для збереження останнього джерела даних
last_source = None

# Функція для отримання ціни з CoinGecko з таймаутом
def get_price_gecko():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    parameters = {
        'ids': 'merkle-trade', 
        'vs_currencies': 'usd',
        'include_24hr_change': 'true'
    }
    
    try:
        response = requests.get(url, params=parameters, timeout=5)  # Таймаут 5 секунд
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from CoinGecko: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        print("Timeout occurred when fetching data from CoinGecko")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Функція для отримання ціни з CoinMarketCap з таймаутом
def get_price_marketcap():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {'symbol': 'MKL', 'convert': 'USD'}
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, params=parameters, timeout=5)  # Таймаут 5 секунд
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from CoinMarketCap: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        print("Timeout occurred when fetching data from CoinMarketCap")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

@tasks.loop(seconds=update_interval)
async def update_price_and_nickname():
    global last_source  # Використовуємо глобальну змінну для збереження останнього джерела
    data = get_price_gecko()
    
    if data is None or 'merkle-trade' not in data:
        # Спробувати отримати ціну з CoinMarketCap
        data = get_price_marketcap()
        if data is None or 'data' not in data:
            print("Error: Unable to fetch price from both APIs.")
            return  # Якщо не вдалося отримати дані з обох API

    # Запис джерела даних у логах
    source = "CoinGecko" if 'merkle-trade' in data else "CoinMarketCap"

    # Якщо джерело змінилося, виводимо в лог
    if source != last_source:
        print(f"Source of price data: {source}")
        last_source = source  # Оновлюємо останнє джерело даних

    # Обробка отриманих даних
    if 'merkle-trade' in data:
        price = data['merkle-trade']['usd']
        change_24h = data['merkle-trade']['usd_24h_change']
    else:
        price = data['data']['MKL']['quote']['USD']['price']
        change_24h = data['data']['MKL']['quote']['USD']['percent_change_24h']

    # Визначення кольорового емодзі для зростання або падіння ціни
    change_symbol = "🟢" if change_24h >= 0 else "🔴"

    # Оновлення нікнейму бота з поточною ціною
    for guild in client.guilds:
        await guild.me.edit(nick=f"${price:,.3f}")  # Тепер показує 3 цифри після коми

    # Оновлення статусу з інформацією про зміну за 24 години
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"24h:{change_symbol}{abs(change_24h):.1f}%"
    ))

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    update_price_and_nickname.start()

# Запуск Discord бота
client.run(DISCORD_TOKEN)
