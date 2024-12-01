# MKL Price Discord Bot

## Description
This Discord bot automatically updates the bot's nickname on the Discord server to show the current MKL (Merkle Trade) cryptocurrency price in USD. The price is retrieved via the CoinGecko and CoinMarketCap APIs, with a fallback mechanism to ensure reliability. Additionally, the bot updates its status regularly to display the change in price over the last 24 hours.

## Key Features
- Updates nickname with MKL price in USD.
- Displays the percentage change in price over the last 24 hours.
- Fetches price data using both CoinGecko and CoinMarketCap APIs, ensuring data availability.
- Built using `discord.py`, with requests every 1 minute.

## Files
- `price_mkl.py`: Main bot logic.
- `requirements.txt`: Dependencies list for installation via `pip`.
- `.env`: Stores sensitive API keys and tokens (excluded from repository).

## Dependencies
- `discord.py`: For interacting with the Discord API.
- `python-dotenv`: Loads environment variables from `.env`.
- `requests`: Handles API requests to CoinMarketCap.


