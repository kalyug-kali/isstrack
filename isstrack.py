import requests
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler

# Define your Telegram Bot API token
TOKEN = '6289462049:AAHgczooz0_7wBhH5nyP-G288UoPXjVxvmk'

# Initialize the Telegram Bot
bot = telegram.Bot(token=TOKEN)

# Define the ISS location function
def iss_location():
    url = 'http://api.open-notify.org/iss-now.json'
    response = requests.get(url)
    data = response.json()
    position = data['iss_position']
    latitude = position['latitude']
    longitude = position['longitude']
    return (latitude, longitude)

# Define the function to get the ISS location and NASA image
api_key = 'Jx6WTMnXfGdYkqDli5GlKm02krvZVQcwKpbh06dj'

def get_iss_location_nasa():
    url = 'http://api.open-notify.org/iss-now.json'
    response = requests.get(url)
    data = response.json()
    latitude = data['iss_position']['latitude']
    longitude = data['iss_position']['longitude']
    nasa_url = f'https://api.nasa.gov/planetary/earth/assets?lon={longitude}&lat={latitude}&dim=0.5&date=2023-03-28&api_key=Jx6WTMnXfGdYkqDli5GlKm02krvZVQcwKpbh06dj'
    nasa_response = requests.get(nasa_url)
    nasa_data = nasa_response.json()
    if 'error' in nasa_data:
        return (latitude, longitude, None)
    elif len(nasa_data.get('results', [])) > 0:
        image_url = nasa_data['results'][0]['url']
        return (latitude, longitude, image_url)
    else:
        # If no image is found for the location, get a random space image
        random_image_data = get_random_space_image(api_key)
        if random_image_data:
            return (latitude, longitude, random_image_data['url'])
        else:
            return (latitude, longitude, None)


# Define the function to get the location name
def get_location_name(latitude, longitude):
    url = f'https://api.bigdatacloud.net/data/reverse-geocode-client'
    response = requests.get(url)
    data = response.json()
    if data.get('locality'):
        return data['locality']
    else:
        return None

# Define the command handler for the '/start' command
def start(update, context):
    update.message.reply_text("Type '/iss' to get the current position of the ISS or 'q' to quit:")

# Define the command handler for the '/iss' command
def iss(update, context):
    latitude, longitude, image_url = get_iss_location_nasa()
    location_name = get_location_name(latitude, longitude)
    message = f"Current ISS Location:\nLatitude: {latitude}\nLongitude: {longitude}\n"
    if location_name:
        message += f"Location Name: {location_name}\n"
    else:
        message += "Location Name not found.\n"
    if image_url:
        message += f"Image URL: {image_url}"
    else:
        message += "No image available."
    update.message.reply_text(message)
def get_random_space_image(api_key):
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&count=1"
    response = requests.get(url)
    if response.status_code == 200:
        images = response.json()
        return images[0]
    else:
        return None

# Define the command handler for unknown commands
def unknown(update, context):
    update.message.reply_text("Invalid command, try again.")

# Initialize the Telegram updater and add the command handlers
updater = Updater(token=TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('iss', iss))
updater.dispatcher.add_handler(CommandHandler('help', start))
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Start the Telegram bot
updater.start_polling()
updater.idle()
