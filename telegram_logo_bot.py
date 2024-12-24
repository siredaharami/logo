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
    photo = await event.download_media(file=bytes)
    users_data[event.chat_id] = {'photo': photo, 'text': '', 'color': 'black', 'position': (10, 10)}

    await update_image_with_text(event, "I got the image! Now send me your logo text.")

async def update_image_with_text(event, message):
    chat_id = event.chat_id
    data = users_data.get(chat_id)
    if not data:
        return

    # Create an image with text
    image = Image.open(io.BytesIO(data['photo']))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 40)
    draw.text(data['position'], data['text'], fill=data['color'], font=font)

    buf = io.BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)

    # Send updated image with buttons
    await client.send_file(
        chat_id,
        buf,
        caption=message,
        buttons=[
            [Button.inline('LEFT ⬅️', b'left'), Button.inline('RIGHT ➡️', b'right')],
            [Button.inline('UP ⬆️', b'up'), Button.inline('DOWN ⬇️', b'down')],
            [Button.inline('RED', b'red'), Button.inline('GREEN', b'green'), Button.inline('BLUE', b'blue'), Button.inline('BLACK', b'black')]
        ]
    )

@client.on(events.NewMessage(func=lambda e: e.text and e.chat_id in users_data))
async def handle_text(event):
    chat_id = event.chat_id
    users_data[chat_id]['text'] = event.raw_text
    await update_image_with_text(event, "Text added! Choose a color or position.")

@client.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode('utf-8')
    chat_id = event.chat_id
    user_data = users_data.get(chat_id)

    if not user_data:
        return

    if data in ['left', 'right', 'up', 'down']:
        x, y = user_data['position']
        if data == 'left':
            x -= 10
        elif data == 'right':
            x += 10
        elif data == 'up':
            y -= 10
        elif data == 'down':
            y += 10
        user_data['position'] = (x, y)

    elif data in ['red', 'green', 'blue', 'black']:
        user_data['color'] = data

    await update_image_with_text(event, "Text updated!")

client.run_until_disconnected()
