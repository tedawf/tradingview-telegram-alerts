# TradingView Telegram Alerts

A real-time trading alert system that integrates **TradingView** with **Telegram**, allowing traders to receive customized market notifications directly on Telegram in real-time.

![Mobile screenshot](demo.png)

## Features

- **Real-time Customizable Alerts**: Receive instant text alerts or real-time snapshot of charts from TradingView to a Telegram chat based on any market conditions you set.
- **FastAPI Webhook**: Lightweight, high-performance webhook built using FastAPI to handle TradingView alerts.
- **Telegram Bot API**: Alerts are pushed directly to any of your Telegram channel chats via the Telegram Bot API for seamless, 24/7 monitoring.

## Try It Out!

1. Clone this repository:

```bash
git clone https://github.com/tedawf/tradingview-telegram-alerts.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your .env file:

- Add your Telegram Bot API token and channel chat ID.
- Add the PORT number

4. Run the FastAPI application:

```bash
uvicorn main:app --reload
```

## Tech Stack

- **FastAPI** – A modern, fast (high-performance) web framework for Python.
- **fly.io** – A powerful platform used to deploy the application, enabling easy scaling and global deployment.
- **Telegram Bot API** – Sends alerts to Telegram chats.
- **Selenium** – A headless brower to programmatically take screenshots of the charts.

## Future Improvements

- Add a more detailed configuration interface for easier setup.
- Explore adding support for multiple Telegram users or groups.
- Add logging and error handling for better alert tracking.

Feel free to contribute or fork this repository!
