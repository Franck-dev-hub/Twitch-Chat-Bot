#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 10/03/2025 by Franck
"""

# Import modules
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
import asyncio
import random
import crypted

# Constants
APP_ID = crypted.client_id
APP_SECRET = crypted.client_secret
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]
TARGET_CHANNEL = crypted.target_channel

async def on_ready(ready_event: EventData):
    # Connect to TARGET_CHANNEL
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # Ready message
    print("Chat Bot ready")

async def lurk_command(cmd: ChatCommand):
    messages = [
        f'Thanks for lurking @{cmd.user.display_name}, I appreciate it.',
        f'Thanks for lurking @{cmd.user.display_name}, You are awesome.',
        f'Thanks for lurking @{cmd.user.display_name}, You are amazing.',
        f'Thanks for lurking @{cmd.user.display_name}, You are the best.',
        f'Thanks for lurking @{cmd.user.display_name}, You are the best viewer.'
    ]

    await cmd.reply(random.choice(messages))

async def on_message(msg: ChatMessage):
    # Print username and chat message into the terminal
    print(f'{msg.user.display_name} >>> {msg.text}')

async def run_bot():
    # Authenticate application
    bot = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)

    # Initialize chat class
    chat = await Chat(bot)

    # Register events
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    # Register commands
    chat.register_command('lurk', lurk_command)

    # Start the chat bot
    chat.start()

    try:
        input('Press ENTER to stop the chat bot\n')
    finally:
        chat.stop()
        await bot.close()

def main():
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()
