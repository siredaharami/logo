from telethon import TelegramClient, events, Button
from PIL import Image, ImageDraw, ImageFont
import io

# Use your own credentials
api_id = 25742938
api_hash = b35b715fe8dc0a58e8048988286fc5b6
bot_token = "7796646089:AAG3yoXJRSI-D2A5w1kPraju_qpL_Xt3JO8"

client = TelegramClient('logo_maker_bot', api_id, api_hash).start(bot_token=bot_token)

users_data = {}

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Welcome to the Logo Maker Bot! Please send me an image.")

@client.on(events.NewMessage(func=lambda e: e.photo))
async def handle_photo(event):
    photo = await event.download_media(file=bytes)
    users_data[event.chat_id] = {'photo': photo}

    await event.respond("I got the image! Now send me the text you want to add to the image.")

@client.on(events.NewMessage)
async def handle_text(event):
    chat_id = event.chat_id
    if chat_id in users_data and 'photo' in users_data[chat_id]:
        text = event.raw_text
        users_data[chat_id]['text'] = text
        users_data[chat_id]['color'] = 'black'
        users_data[chat_id]['position'] = (10, 10)
        users_data[chat_id]['font_path'] = "arial.ttf"

        await event.respond(
            "Choose an option:",
            buttons=[
                [Button.inline("Color", b'color'), Button.inline("Font", b'font')],
                [Button.inline("Move", b'move'), Button.inline("Create", b'create')],
            ]
        )

@client.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode("utf-8")
    chat_id = event.chat_id
    
    if data == 'color':
        await event.respond(
            "Select a color:",
            buttons=[
                [Button.inline("Red", b'set_color_red'), Button.inline("Green", b'set_color_green'), Button.inline("Blue", b'set_color_blue')],
                [Button.inline("Black", b'set_color_black'), Button.inline("White", b'set_color_white')],
            ]
        )
    
    elif data.startswith('set_color_'):
        color = data.split('_')[-1]
        users_data[chat_id]['color'] = color
        await event.answer(f"Color set to {color}", alert=True)

    elif data == 'font':
        await event.respond(
            "Select a font:",
            buttons=[
                [Button.inline("Font A", b'set_font_a'), Button.inline("Font B", b'set_font_b')],
                [Button.inline("Font C", b'set_font_c')]
            ]
        )

    elif data.startswith('set_font_'):
        font_choice = data.split('_')[-1]
        font_paths = {
            'a': "arial.ttf",
            'b': "times.ttf",  # Ensure these fonts are available
            'c': "courier.ttf"
        }
        users_data[chat_id]['font_path'] = font_paths.get(font_choice, "arial.ttf")
        await event.answer(f"Font set to {font_choice.upper()}", alert=True)

    elif data == 'move':
        await event.respond(
            "Move text:",
            buttons=[
                [Button.inline("Left", b'move_left'), Button.inline("Right", b'move_right')],
                [Button.inline("Up", b'move_up'), Button.inline("Down", b'move_down')],
            ]
        )

    elif data.startswith('move_'):
        direction = data.split('_')[-1]
        x, y = users_data[chat_id]['position']
        
        if direction == 'left':
            x -= 10
        elif direction == 'right':
            x += 10
        elif direction == 'up':
            y -= 10
        elif direction == 'down':
            y += 10
        
        users_data[chat_id]['position'] = (x, y)
        await event.answer(f"Moved {direction}", alert=True)

    elif data == 'create':
        await create_logo(event, chat_id)

async def create_logo(event, chat_id):
    if chat_id in users_data:
        photo = users_data[chat_id]['photo']
        text = users_data[chat_id]['text']
        color = users_data[chat_id]['color']
        position = users_data[chat_id]['position']
        font_path = users_data[chat_id]['font_path']

        image = Image.open(io.BytesIO(photo))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, 40)

        draw.text(position, text, fill=color, font=font)

        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)

        await client.send_file(chat_id, buf, caption="Here is your logo!")

client.run_until_disconnected()
