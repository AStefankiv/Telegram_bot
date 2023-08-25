import logging
import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes
import requests


logging.basicConfig(level=logging.INFO)
DATE_INPUT, TIME_INPUT = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.first_name
    message = (
        f"Hi {user}! I'm your lesson booking bot.\n"
        f"Here are the available commands:"
    )

    keyboard = [
        ["/hello", "/book_a_lesson", "/more_information"],
        ["/weather", "/cancel"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(message, reply_markup=reply_markup)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'⬇️ Hello {update.effective_user.first_name}. Please go to the "Menu" and select an option.')


async def more_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info_text = (
        "👋Hello, I'm Andrew, and I bring over a decade of English teaching experience to the table. My journey has taken me to classrooms across four different countries spanning three continents.\n \n 🍁Presently, I'm based in Calgary, Canada, where I am an educator at the esteemed 'Global Village' school. Interacting with students from diverse nationalities and age groups is a point of pride for me.\n \n 👨‍🏫Moreover, I've adeptly conducted online instruction, encompassing both group sessions and one-on-one tutorials. If you're looking to enhance your English skills, I warmly invite you to reserve a trial class with me. Let's embark on this language-learning journey together!\n\n"
        "For more information, you can connect with me on [Facebook](https://www.facebook.com/andrii.stefankiv/) or reach out via email at stefankif35@gmail.com."
    )
    await update.message.reply_text(info_text, parse_mode="Markdown", disable_web_page_preview=False)


async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    today = datetime.date.today()
    next_10_days = [today + datetime.timedelta(days=i) for i in range(10)]
    date_options = [date.strftime("%d %B %Y") for date in next_10_days]

    if len(date_options) % 2 != 0:
        date_options.append("")

    context.user_data["date_options"] = date_options

    keyboard = [[date_options[i], date_options[i + 1]] for i in range(0, len(date_options), 2)]
    keyboard.append(["Cancel"])
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Please select a booking date:", reply_markup=reply_markup)
    return DATE_INPUT

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    input_date = update.message.text

    if input_date in context.user_data.get("date_options", []):
        context.user_data["date"] = input_date
        await update.message.reply_text(f"You chose: {input_date}")

        keyboard = [["11 AM", "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM"], ["Cancel"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please select a booking time:", reply_markup=reply_markup)
        return TIME_INPUT
    else:
        await update.message.reply_text("Invalid option. Please select a valid date option from the provided list.")
        return DATE_INPUT


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    time = update.message.text
    context.user_data["time"] = time
    chosen_date = context.user_data.get("date", "Unknown")

    formatted_date = datetime.datetime.strptime(chosen_date, "%d %B %Y").strftime("%Y%m%d")
    formatted_time = datetime.datetime.strptime(time, "%I %p").strftime("%H%M%S")

    end_time = (datetime.datetime.strptime(time, "%I %p") + datetime.timedelta(hours=1)).strftime("%H%M%S")

    event_title = "Your Lesson with teacher Andrew"
    calendar_link = (
        f"https://www.google.com/calendar/event?action=TEMPLATE"
        f"&text={event_title}&dates={formatted_date}T{formatted_time}/{formatted_date}T{end_time}"
    )

    zoom_link = "https://us06web.zoom.us/j/8182736518?pwd=U2E0bEp3alduWFFqbkF1THdrWDNhUT09"
    meeting_id = "818 273 6518"
    passcode = "11111"

    keyboard = [[InlineKeyboardButton("Add to Google Calendar", url=calendar_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"📚 Your lesson will be on {chosen_date.capitalize()} at {time}.\n"
        f"🎥 Here's the Zoom link: {zoom_link}.\n"
        f"✔️Meeting ID: {meeting_id}\n"
        f"✔️Passcode: {passcode}\n"
        "\n"
        f"📅You can also add this event to your Google Calendar:⬇️"
    )
    await update.message.reply_text(message, reply_markup=reply_markup)
    return ConversationHandler.END


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city_name = "Calgary"  # You can customize the city here
    weather_data = get_weather(city_name)

    temperature = weather_data['main']['temp']
    weather_description = weather_data['weather'][0]['description']

    message = (
        f'🌤️ Weather in {city_name}:\n'
        f'Temperature: {temperature}°C\n'
        f'Conditions: {weather_description}'
    )

    await update.message.reply_text(message)


# Place your API key here
API_KEY = '5d03de9143d8f66e4da9cd4ff4be7cfc'

# URL for the OpenWeatherMap API
API_URL = f'http://api.openweathermap.org/data/2.5/weather'


# Function to fetch weather data
def get_weather(city_name):
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric',
    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    return data

def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text("Booking canceled.", reply_markup=ReplyKeyboardRemove())

app = ApplicationBuilder().token("5945953214:AAEcfnBgUY5A63qNWl1nKQjPNDurax7dRrs").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("more_information", more_information))
app.add_handler(CommandHandler("cancel", cancel))
app.add_handler(CommandHandler("weather", weather))


booking_date_handler = ConversationHandler(
    entry_points=[CommandHandler('book_a_lesson', start_booking)],
    states={
        DATE_INPUT: [MessageHandler(None, get_date)],
        TIME_INPUT: [MessageHandler(None, get_time)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
app.add_handler(booking_date_handler)

if __name__ == "__main__":
    app.run_polling()