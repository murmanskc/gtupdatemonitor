import os
import requests
from steam.client import SteamClient

APP_ID = 866020 # Growtopia's App ID
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "last_changenumber.txt"

def get_changenumber():
    try:
        print("Connecting directly to Steam's network...")
        client = SteamClient()
        client.anonymous_login()
        
        info = client.get_product_info(apps=[APP_ID])
        client.logout()

        if info and 'apps' in info and APP_ID in info['apps']:
            app_data = info['apps'][APP_ID]
            
            # Found the exact key Valve uses!
            changenumber = app_data.get('_change_number')
            
            if changenumber:
                return str(changenumber)

        print("Failed to find _change_number in Steam response.")
        return None
    except Exception as e:
        print(f"Error connecting to Steam: {e}")
        return None

def send_discord_alert(old_num, new_num):
    if not WEBHOOK_URL:
        print("No Discord webhook configured!")
        return

    message = {
        "content": f"🚨 **Growtopia Update Detected!** 🚨\n\n**Old Changenumber:** {old_num}\n**New Changenumber:** {new_num}\n\n*(Data pulled directly from Steam's network)*\nCheck manually: https://steamdb.info/app/{APP_ID}/info/"
    }
    
    requests.post(WEBHOOK_URL, json=message)

def main():
    current_number = get_changenumber()
    if not current_number:
        return

    print(f"Current Changenumber found: {current_number}")

    last_number = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_number = f.read().strip()

    if current_number != last_number:
        print("Change detected! Sending alert...")
        if last_number != "":
            send_discord_alert(last_number, current_number)
        
        with open(STATE_FILE, "w") as f:
            f.write(current_number)
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
