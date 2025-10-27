import websocket
import time
import threading
import asyncio
import re
import json
from utils import get_main_file_path
from discord.ext import commands
from typing import List

WS_API_ENDPOINT: str = 'wss://api.synoptic.com/v1/ws'
with open(get_main_file_path().parent / 'synoptic_api_key.secret', 'r', encoding='utf-8') as f:
    API_KEY: str = f.read().strip()
RECONNECT_DELAY_SEC: int = 1

# run_ws_async() from https://synoptic.com/p/streams/01JEYDKB3PH1WJ1BANH2V0H9HP/reader-api
# with minor modifications
class TruthSocialWS:
    def __init__(self, client: commands.Bot, truth_social_channel_ids: List[int]) -> None:
        self.client = client
        self.truth_social_channel_ids = truth_social_channel_ids
        thread = threading.Thread(target=self.run_ws, daemon=True)
        thread.start()
        print('Truth Social WebSocket thread initialized')

    @staticmethod
    def parse_truth_post(message: str) -> tuple[str | None, str | None, str | None]:
        # Extract the link and type lines
        link_match = re.search(r'Link:\s*(\S+)', message)
        type_match = re.search(r'Type:\s*(\w+)', message)

        # Everything before "Link:" is treated as the post text/media
        # (strip() cleans up blank lines and spaces)
        text_part = message.split("Link:")[0].strip()

        text_or_media = text_part if text_part else None
        link = link_match.group(1) if link_match else None
        post_type = type_match.group(1).lower() if type_match else None

        return text_or_media, link, post_type

    @staticmethod
    def process_truth_post(message: str) -> tuple[bool, str]:
        text_or_media, link, post_type = TruthSocialWS.parse_truth_post(message)

        if post_type is None:
            return False, 'Error: Post type not found.'
        
        if post_type == 'reply':
            return False, 'Ignoring reply post.'
        
        if text_or_media is None or link is None:
            return False, 'Error: Incomplete post data.'
        
        formatted_post = '**New Truth from Donald J. Trump, 47th President of the United States of America**\n'

        if post_type == 'quote':
            quoted = text_or_media.split(' ')[1]
            content = ' '.join(text_or_media.split(' ')[2:]).strip()
            formatted_post += f'Quoted {quoted}\n{content}\n'
        elif post_type == 'repost':
            reposted = f'@{text_or_media.split(" ")[2].strip()}'
            content = ' '.join(text_or_media.split(' ')[3:]).strip()
            formatted_post += f'ReTruthed from {reposted}\n{content}\n'
        elif post_type == 'post':
            formatted_post += f'{text_or_media}\n'
        else:
            return False, f'Error: Unknown post type "{post_type}".'
        
        formatted_post += f'Original Post: {link}\n*Data by Synoptic.com*'
        return True, formatted_post

    async def on_truth_social_post(self, post: str) -> None:
        for channel_id in self.truth_social_channel_ids:
            channel = self.client.get_channel(channel_id)
            if not channel:
                print("Truth Social channel not found. Make sure the bot can see it.")
                return

            await channel.send(post)

    def schedule_truth_post(self, post: str) -> None:
        try:
            loop = self.client.loop
            loop.call_soon_threadsafe(
                asyncio.create_task, self.on_truth_social_post(post)
            )
        except Exception as e:
            print(f"Error scheduling Truth Social post: {e}")

    def run_ws(self) -> None:
        ws_url = f"{WS_API_ENDPOINT}/on-stream-post?apiKey={API_KEY}"

        while True:
            try:
                ws = websocket.create_connection(ws_url)
                print('WebSocket connected to the server')
                while True:
                    try:
                        message = ws.recv()
                        if message is None:
                            print('WebSocket connection closed by server')
                            break

                        json_msg = json.loads(message)
                        if json_msg['event'] != 'stream.post.created':
                            continue

                        success, processed_post = TruthSocialWS.process_truth_post(json_msg['data']['text'])
                        if success:
                            self.schedule_truth_post(processed_post)
                        else:
                            print(processed_post)  # On failure, this is actually an error message
                    except websocket.WebSocketConnectionClosedException:
                        print('WebSocket connection closed')
                        break
                    except Exception as e:
                        print('WebSocket error:', e)
                        break
            except Exception as e:
                print('WebSocket connection failed:', e)
            finally:
                try:
                    ws.close()
                except Exception:
                    pass
                print(f"Reconnecting in {RECONNECT_DELAY_SEC} seconds...")
                time.sleep(RECONNECT_DELAY_SEC)

    client: commands.Bot
    truth_social_channel_ids: List[int]
