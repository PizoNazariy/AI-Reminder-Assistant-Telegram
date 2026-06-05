![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-orange)


# AI-Reminder-Assistant-Telegram
This is a Telegram bot with the main function of reminders, using Groq Artificial Intelligence through an API and the code is written in Python.

## ✨ Advantages

- 💬 **Natural conversation**

  No need to learn any commands. You can say *"today I need to buy bread"* or *"I already called the doctor"* and the bot understands on its own. Just like talking to a real person.

- 🧠 **Integrated artificial intelligence**

  Uses a language model (Groq) to understand the context of the conversation. It understands synonyms, incomplete sentences, and even the user's mood.

- 🔔 **Periodic reminders**

  The bot automatically notifies you every X time about your pending tasks, without you having to do anything.

- 👥 **Multi-user**

  Every person who talks to the bot has their own completely separate task list. Many people can use it at the same time.

- 💾 **Data persistence**

  Tasks are saved in a local `tasks.json` file. If you stop the bot and start it again, your tasks are still there.

- 🗣️ **Conversation memory**

  The bot remembers the conversation thread (last 20 messages) to give coherent and contextual responses. Completed reminders have a 10-day period to review and manage their completion.

- 🌍 **Multilingual**

  Responds in the same language the user writes in — Catalan, Spanish, English, and more.


##  📁 Structure
```
Reminder_Bot/
├── bot.py          # Principal code Bot 
├── .env            # API keys
└── recordatorios.json  #Reminders
```

## 🛠️ Tech stack

- **Python 3.10+** — Main language
- **python-telegram-bot** — Telegram API connection
- **Groq** — AI for natural language processing (model `llama-3.3-70b-versatile`)
- **APScheduler** — Scheduler to send reminders automatically
- **python-dotenv** — Environment variables management

## 📦 Dependencies

```
python-telegram-bot
groq
python-dotenv
apscheduler
```

## ⚙️ How it works

1. The user sends a natural language message to the bot
2. Groq interprets the message and extracts the intent (add, delete, list)
3. The reminder is saved to the `recordatorios.json` file
4. Every minute the scheduler checks for pending reminders and sends them
5. Completed reminders are automatically deleted after 10 days

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Telegram account
- Groq API key — [console.groq.com](https://console.groq.com)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/your-username/Reminder_Bot.git
cd Reminder_Bot
```

**2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure API keys**
```bash
cp .env.example .env
nano .env
```
```
TELEGRAM_TOKEN=your_telegram_token_here
GROQ_API_KEY=your_groq_api_key_here
```

**5. Create data file**
```bash
echo "[]" > recordatorios.json
```

**6. Run the bot**
```bash
python bot.py
```

### Run as a system service (Raspberry Pi)
```bash
sudo cp config/reminder-bot.service /etc/systemd/system/
sudo systemctl enable reminder-bot
sudo systemctl start reminder-bot
```
