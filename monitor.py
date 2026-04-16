import requests
from bs4 import BeautifulSoup
import json
import os

# --- Configuration ---
# Replace this with the actual SteamDB URL for Growtopia
STEAMDB_URL = "https://steamdb.info/app/866020/info/" 
# Your Discord Webhook URL (set this in GitHub Secrets)
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK") 
STATE_FILE = "last_changenumber.txt"

def get_current_changenumber():
    # We use a standard browser header to try and bypass basic bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(STEAMDB_URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table row containing "Last Changenumber"
        # SteamDB usually puts this in a <td>, and the number in the next <td>
        changenumber_label = soup.find(text="Last Changenumber")
        
        if changenumber_label:
            # Navigate to the parent element, then find the value
            # Note: HTML structure might require tweaking if SteamDB updates their layout
            parent_row = changenumber_label.find_parent('tr') 
            if parent_row:
                value_td = parent_row.find_all('td')[1]
                return value_td.text.strip()
                
        print("Could not find the changenumber on the page. Cloudflare might be blocking the request.")
        return None
        
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

def send_discord_alert(old_num, new_num):
    if not WEBHOOK_URL:
        print("No Discord webhook configured!")
        return

    message = {
        "content": f"🚨 **Growtopia Update Detected on SteamDB!** 🚨\n\n**Old Changenumber:** {old_num}\n**New Changenumber:** {new_num}\n\nCheck it here: {STEAMDB_URL}"
    }
    
    requests.post(WEBHOOK_URL, json=message)

def main():
    current_number = get_current_changenumber()
    if not current_number:
        return

    print(f"Current Changenumber found: {current_number}")

    # Read the last known number
    last_number = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_number = f.read().strip()

    # Compare and alert
    if current_number != last_number:
        print("Change detected! Sending alert...")
        if last_number != "": # Don't alert on the very first run
            send_discord_alert(last_number, current_number)
        
        # Save the new number to the file
        with open(STATE_FILE, "w") as f:
            f.write(current_number)
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()