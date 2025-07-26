import random  # This is random bullshit
import logging
import subprocess
import sys
import os
import re
import time
import concurrent.futures
import discord
from discord.ext import commands, tasks
import docker
import asyncio
from discord import app_commands

TOKEN = ''  # TOKEN HERE
RAM_LIMIT = '2g'
SERVER_LIMIT = 12
database_file = 'database.txt'

intents = discord.Intents.default()
intents.messages = False
intents.message_content = False
bot = commands.Bot(command_prefix='/', intents=intents)
client = docker.from_env()

# port gen forward module < i forgot this shit in the start
def generate_random_port():
    return random.randint(1025, 65535)

def add_to_database(user, container_name, ssh_command):
    with open(database_file, 'a') as f:
        f.write(f"{user}|{container_name}|{ssh_command}\n")

def remove_from_database(ssh_command):
    if not os.path.exists(database_file):
        return
    with open(database_file, 'r') as f:
        lines = f.readlines()
    with open(database_file, 'w') as f:
        for line in lines:
            if ssh_command not in line:
                f.write(line)

async def capture_ssh_session_line(process):
    while True:
        output = await process.stdout.readline()
        if not output:
            break
        output = output.decode('utf-8').strip()
        if "ssh session:" in output:
            return output.split("ssh session:")[1].strip()
    return None

def get_ssh_command_from_database(container_id):
    if not os.path.exists(database_file):
        return None
    with open(database_file, 'r') as f:
        for line in f:
            if container_id in line:
                return line.split('|')[2]
    return None

def get_user_servers(user):
    if not os.path.exists(database_file):
        return []
    servers = []
    with open(database_file, 'r') as f:
        for line in f:
            if line.startswith(user):
                servers.append(line.strip())
    return servers

def count_user_servers(user):
    return len(get_user_servers(user))

def get_container_id_from_database(user, container_name):
    if not os.path.exists(database_file):
        return None
    with open(database_file, 'r') as f:
        for line in f:
            if line.startswith(user) and container_name in line:
                return line.split('|')[1]
    return None

@bot.event
async def on_ready():
    change_status.start()
    print(f'Bot is ready. Logged in as {bot.user}')
    for guild in bot.guilds:
        await bot.tree.sync(guild=guild)  # FIXED: Avoid global sync error

@tasks.loop(seconds=5)
async def change_status():
    try:
        if os.path.exists(database_file):
            with open(database_file, 'r') as f:
                lines = f.readlines()
            instance_count = len(lines)
        else:
            instance_count = 0
        status = f"with {instance_count} Cloud Instances"
        await bot.change_presence(activity=discord.Game(name=status))
    except Exception as e:
        print(f"Failed to update status: {e}")

# ... (the rest of your code remains unchanged)

bot.run(TOKEN)
