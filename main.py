# region Init
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 10/03/2025 by Frost_Seeker
"""
# endregion

# region Modules
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent, EventSubSubscriptionConflict, EventSubSubscriptionError
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch

import  twitchAPI.eventsub as EventSub
import pygame
import json
import os
import requests
import asyncio
import random
# endregion

# region Constants
# Charger les informations depuis crypted.json
with open('crypted.json', 'r') as f:
    crypted_data = json.load(f)

APP_ID = crypted_data['client_id']
APP_SECRET = crypted_data['client_secret']
TARGET_CHANNEL = crypted_data['target_channel']
BOT_USERNAME = crypted_data['bot_username']
VLC_PATH = crypted_data['vlc_path']
CALLBACK_URL = crypted_data['callback_url']

TOKEN_FILE = "token.json"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
USER_SCOPE = [
    AuthScope.CHAT_READ,
    AuthScope.CHAT_EDIT,
    AuthScope.CHANNEL_MANAGE_BROADCAST,
    AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
]
# endregion

# region Authentification
async def get_authenticated_bot():
    bot = await Twitch(APP_ID, APP_SECRET)

    # Vérifier si un token existe déjà
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)
            token, refresh_token = tokens["token"], tokens["refresh_token"]
            try:
                await bot.set_user_authentication(token, USER_SCOPE, refresh_token)
                return bot
            except Exception:
                print("Token expiré, rafraîchissement en cours...")

    # Si aucun token ou expiration, authentifier de zéro
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)

    # Sauvegarde des nouveaux tokens
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token, "refresh_token": refresh_token}, f)

    return bot

def refresh_access_token(refresh_token):
    params = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(TOKEN_URL, params)
    new_tokens = response.json()

    if "access_token" in new_tokens:
        return new_tokens["access_token"], new_tokens["refresh_token"]
    else:
        raise Exception(f"Erreur de rafraîchissement : {new_tokens}")
# endregion

# region Events
async def on_ready(ready_event: EventData):
    await ready_event.chat.join_room(TARGET_CHANNEL)
    print("Chat Bot ready")

async def on_join(msg: ChatMessage):
    print(f'Welcome {msg.user.display_name}')

async def on_message(msg: ChatMessage):
    print(f'{msg.user.display_name} >>> {msg.text}')

async def on_follow(data):
    user_name = data["event"]["user_name"]
    print(f'🚀 {user_name} vient de follow !')

    alert_messages = [
        f'🔥 {user_name} a rejoint la tribu ! Bienvenue ! 🎉',
        f'🚀 Merci pour le follow {user_name} ! Profite bien du stream !',
        f'🎊 {user_name} vient de nous rejoindre ! Installe-toi bien !'
    ]
    chat = await Chat(bot)  # Initialiser Chat
    await chat.send_message(TARGET_CHANNEL, random.choice(alert_messages))

async def on_sub(sub: ChatSub):
    print(f'New sub !! :\n'
          f'  Type: {sub.sub_plan}\n'
          f'  Message: {sub.sub_message}')

async def on_raid(raid: EventData):
    print(f'RAIIIIIIIIID !! par {raid.user.display_name}')

def events(event):
    event.register_event(ChatEvent.READY, on_ready)
    event.register_event(ChatEvent.JOIN, on_join)
    event.register_event(ChatEvent.MESSAGE, on_message)
    event.register_event(ChatEvent.SUB, on_sub)
    event.register_event(ChatEvent.RAID, on_raid)
# endregion

# region Commands
async def lurk_command(cmd: ChatCommand):
    messages = [
        f'Merci pour ton lurk @{cmd.user.display_name} la tribu te remercie !',
        f'Merci pour ton lurk @{cmd.user.display_name} tu es génial !',
        f'Merci @{cmd.user.display_name} pour ton soutien légendaire !',
        f'Merci pour ton lurk @{cmd.user.display_name} tu es le meilleur !',
        f'Merci pour ton lurk @{cmd.user.display_name} il n\' a pas meilleur que toi !'
    ]
    await cmd.reply(random.choice(messages))

async def shout_out(cmd: ChatCommand):
    # Récupération du pseudo du streamer
    target_streamer = cmd.parameter.strip() if cmd.parameter else None

    print(f"========================= Shout out =========================\n"
          f"                          {target_streamer}\n"
          f"=============================================================")

    # Si le streamer n'est pas spécifié
    if not target_streamer:
        await cmd.send('Le streamer n\'est pas spécifié pour le shoutout !')
        return

    # Messages de shoutout
    messages = [
        f'Donnes du love à @{target_streamer} et n\'hésites pas à le follow https://www.twitch.tv/{target_streamer}',
        f'Allez voir le stream de @{target_streamer} sur https://www.twitch.tv/{target_streamer}',
    ]
    await cmd.reply(random.choice(messages))

async def test_son(cmd: ChatCommand):
    try:
        sound_path = "sounds/son.wav"  # Chemin vers votre fichier .wav
        if not os.path.exists(sound_path):
            print("Fichier audio introuvable !")
            return

        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()
        await cmd.reply("Son joué ! 🎶")
    except Exception as e:
        print(f"Erreur lors de la lecture du son : {e}")

def commands(event):
    event.register_command('lurk', lurk_command)
    event.register_command('so', shout_out)
    event.register_command('testson', test_son)
# endregion

# region Main
async def run_bot():
    global bot  # Pour utiliser le bot dans EventSub
    bot = await get_authenticated_bot()

    # Initialiser le module de son
    pygame.mixer.init()

    chat = await Chat(bot)
    events(chat)
    commands(chat)

    chat.start()

    try:
        input('Press ENTER to stop the chat bot\n')
    finally:
        chat.stop()
        await bot.close()

def main():
    asyncio.run(run_bot())

    new_token, new_refresh_token = refresh_access_token("TON_REFRESH_TOKEN")
    print(f"Nouveau Token: {new_token}")

if __name__ == "__main__":
    main()
# endregion