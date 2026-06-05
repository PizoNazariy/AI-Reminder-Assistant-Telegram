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

Reminder_Bot/
├── bot.py          # Principal code Bot 
├── .env            # API keys
└── recordatorios.json  #Reminders
