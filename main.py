from discord_webhook import DiscordWebhook, DiscordEmbed
import subprocess
import re
import os
import configparser

#function for load properties from .properties 
def load_properties(file_path):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    return config

#load properties
config = load_properties('.properties')
WEBHOOK_URL = config['webhook']['url']
LAUNCHER = config['webhook']['launcher']

#extract player chatting from server log
def parse_log(log_file):
    match = re.search(r'\[\d{2}:\d{2}:\d{2}\] \[Server thread/INFO\] \[minecraft/MinecraftServer\]: <(.+)> (.+)', log_file)
    if match:
        user_id = match.group(1)
        message = match.group(2)
        return user_id, message
    return None, None

def send_to_discord(user_id, message):
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    
    embed = DiscordEmbed(title=user_id, color='03b2f8')
    embed.add_embed_field(name='',value=message, inline=False)
    
    webhook.add_embed(embed)
    response = webhook.execute()
    
    if response.status_code != 200:
        print(f"Error sending message to Discord: {response.status_code}, {response.content}")

def try_decode(output):
    try:
        return output.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            return output.decode('cp949').strip()
        except UnicodeDecodeError:
            return output.decode('latin-1').strip()

def run_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            log_line = try_decode(output)
            user_id, message = parse_log(log_line)
            if user_id and message:
                send_to_discord(user_id, message)
            else:
                print(log_line)
    rc = process.poll()
    return rc

run_command(['cmd', '/c', LAUNCHER])
