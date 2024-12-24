from telethon import TelegramClient, events, Button
from PIL import Image, ImageDraw, ImageFont
import io

# Use your own values here
api_id = 25742938
api_hash = "b35b715fe8dc0a58e8048988286fc5b6"
bot_token = "7796646089:AAG3yoXJRSI-D2A5w1kPraju_qpL_Xt3JO8"

client = TelegramClient('logo_maker_bot', api_id, api_hash).start(bot_token=bot_token)

users_data = {}

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Welcome to the Logo Maker Bot!\nPlease send me an image.")

@client.on(events.NewMessage(func=lambda e: e.photo))
async def handle_photo(event):
    # Download the image
    photo = await event.download_media(file=bytes)
    users_data[event.chat_id] = {'photo': photo}
    await event.respond("I got the image! Now send me the text you want to add to the image.")

@client.on(events.NewMessage)
async def handle_text(event):
    chat_id = event.chat_id
    if chat_id in users_data and 'photo' in users_data[chat_id]:
        text = event.raw_text
        users_data[chat_id]['text'] = text

        # Send inline keyboard for color selection
        await event.respond(
            "Please choose a color for the text:",
            buttons=[
                [Button.inline("Red", b'red'), Button.inline("Green", b'green'), Button.inline("Blue", b'blue')],
                [Button.inline("Black", b'black'), Button.inline("White", b'white')]
            ]
        )

@client.on(events.CallbackQuery)
async def handle_callback_query(event):
    color = event.data.decode("utf-8")
    chat_id = event.chat_id

    if chat_id in users_data and 'photo' in users_data[chat_id] and 'text' in users_data[chat_id]:
        # Retrieve photo and text
        photo = users_data[chat_id]['photo']
        text = users_data[chat_id]['text']

        # Open image and draw text
        image = Image.open(io.BytesIO(photo))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 40)

        # Draw the text on the image
        draw.text((10, 10), text, fill=color, font=font)

        # Save the image to a bytes buffer
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)

        # Send the image back
        await client.send_file(chat_id, buf, caption="Here is your logo!")
        await event.answer("Logo created!")

# Run the client
client.run_until_disconnected()
