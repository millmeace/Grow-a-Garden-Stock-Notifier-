import requests  
from bs4 import BeautifulSoup  
from datetime import datetime, timedelta  
import time  
import sys  
import os  

service_was_down = False
last_down_notification_time = None

# Color map dictionary
color_map = {
    "Carrot": "4CAF50", "Strawberry": "4CAF50", "Blueberry": "4CAF50", "Orange": "4CAF50",
    "Tomato": "8BC34A", "Corn": "8BC34A", "Daffodil": "8BC34A",
    "Watermelon": "FFC107", "Pumpkin": "FFC107", "Apple": "FFC107", "Bamboo": "FFC107",
    "Coconut": "FF9800", "Cactus": "FF9800", "Dragon": "FF9800", "Mango": "FF9800",
    "Grape": "9C27B0", "Mushroom": "9C27B0", "Pepper": "9C27B0", "Cacao": "9C27B0",
    "Beanstalk": "00BCD4", "Ember Lily": "00BCD4", "Sugar Apple": "00BCD4", "Burning Bud": "00BCD4", 
    "Giant Pinecone": "00BCD4", "Watering": "4CAF50", "Trowel": "4CAF50", "Recall": "4CAF50",
    "Basic": "FFC107",
    "Advanced": "9C27B0",
    "Lightning": "FF9800", "Godly": "FF9800",
    "Harvest": "673AB7", "Master": "673AB7", "Favorite": "673AB7",
    "Common Egg": "4CAF50", "Uncommon Egg": "8BC34A",
    "Legendary Egg": "9C27B0", "Bug Egg": "FF5722", "Mythical Egg": "FF9800",
    "Flower Seed Pack": "4CAF50",
    "Nectarine Seed": "FF9800",
    "Hive Fruit Seed": "FFEB3B",
    "Honey Sprinkler": "FF9800",
    "Bee Egg": "FF9800",
    "Bee Crate": "9C27B0",
    "Brick Stack": "4CAF50",
    "Compost Bin": "4CAF50",
    "Log": "4CAF50",
    "Wood Pile": "4CAF50",
    "Torch": "4CAF50",
    "Circle Tile": "4CAF50",
    "Path Tile": "4CAF50",
    "Rock Pile": "4CAF50",
    "Pottery": "4CAF50",
    "Rake": "4CAF50",
    "Umbrella": "4CAF50",
    "Log Bench": "2196F3",
    "Brown Bench": "2196F3",
    "White Bench": "2196F3",
    "Hay Bale": "2196F3",
    "Stone Pad": "2196F3",
    "Stone Table": "2196F3",
    "Wood Fence": "2196F3",
    "Wood Flooring": "2196F3",
    "Mini TV": "2196F3",
    "Viney Beam": "2196F3",
    "Light On Ground": "2196F3",
    "Water Trough": "2196F3",
    "Shovel Grave": "2196F3",
    "Stone Lantern": "2196F3",
    "Bookshelf": "2196F3",
    "Axe Stump": "2196F3",
    "Stone Pillar": "9C27B0",
    "Wood Table": "9C27B0",
    "Canopy": "9C27B0",
    "Campfire": "9C27B0",
    "Cooking Pot": "9C27B0",
    "Clothesline": "9C27B0",
    "Wood Arbour": "FFEB3B",
    "Metal Arbour": "FFEB3B",
    "Bird Bath": "9C27B0",
    "Lamp Post": "9C27B0",
    "Wind Chime": "9C27B0",
    "Well": "FFEB3B",
    "Ring Walkway": "FFEB3B",
    "Tractor": "FFEB3B",
    "Honey Comb": "FF9800",
    "Honey Torch": "FF9800",
    "Bee Chair": "FF9800",
    "Honey Walkway": "FF9800",
    "Gnome Crate": "795548",
    "Sign Crate": "795548",
    "Bloodmoon Crate": "795548",
    "Twilight Crate": "795548",
    "Mysterious Crate": "795548",
    "Fun Crate": "795548",
    "Monster Mash Trophy": "FF5722"
}

# Items to notify about (add the ones you want notifications for)
notify_items = [
    "Cactus", "Melon", "Ember Lily", "Friendship Pot", "Honey Sprinkler", "Bee Egg", "Sunflower", "Nectarine", "Hive Fruit", "Dragon", "Mango", "Grape", "Mushroom", "Pepper", "Cacao",
    "Beanstalk", "Godly", "Bug Egg", "Mythical Egg",
    "Bee Crate", "Stone Pillar", "Bird Bath", "Lamp Post", "Tractor", "Master Sprinkler", "Lightning Rod"
]

# Track previously seen items to avoid duplicate notifications
previous_stock = set()

def clear_screen():  
    os.system("cls" if os.name == "nt" else "clear")  
  
def print_border(text):  
    width = len(text) + 4  
    print("╔" + "═" * (width - 2) + "╗")  
    print(f"║ {text} ║")  
    print("╚" + "═" * (width - 2) + "╝")  

def get_color_escape(rgb_hex, background=False):
    """Return ANSI escape code for the given RGB hex color"""
    r = int(rgb_hex[0:2], 16)
    g = int(rgb_hex[2:4], 16)
    b = int(rgb_hex[4:6], 16)
    return f'\033[{"48" if background else "38"};2;{r};{g};{b}m'

def colorize_text(text, rgb_hex):
    """Colorize text with the given RGB hex color"""
    color_code = get_color_escape(rgb_hex)
    reset_code = '\033[0m'
    return f"{color_code}{text}{reset_code}"

last_ntfy_limit_time = None
ntfy_on_cooldown = False

def send_push_notification(title, message):
    global last_ntfy_limit_time, ntfy_on_cooldown
    try:
        if ntfy_on_cooldown and datetime.now() - last_ntfy_limit_time < timedelta(minutes=60):
            print("⚠️ Skipped notification: ntfy.sh is on cooldown")
            return

        url = "https://ntfy.sh/seed_stock_bot"
        response = requests.post(url, data=message, headers={"Title": title})

        if response.status_code == 429:
            print("❌ ntfy.sh rate limit hit!")
            last_ntfy_limit_time = datetime.now()
            ntfy_on_cooldown = True
        else:
            print(f"✅ Notification sent: {title} - {message}")
            ntfy_on_cooldown = False
            last_ntfy_limit_time = None
    except Exception as e:
        print(f"Failed to send notification: {e}")

def scrape_stock():  
    global previous_stock, service_was_down, last_down_notification_time
    current_stock = set()
    items_to_notify = []
    
    clear_screen()  
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')  
    print_border(f" STOCK CHECK - {now_str} ")  
  
    url = "https://vulcanvalues.com/grow-a-garden/stock"  
    headers = {"User-Agent": "Mozilla/5.0"}  

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception("Non-200 status code")

        soup = BeautifulSoup(response.text, "html.parser")  

        any_stock_found = False
        for header in soup.find_all("h2"):  
            if header.text.strip().endswith("STOCK"):  
                ul = header.find_next_sibling("ul")  
                if ul:  
                    any_stock_found = True
                    print(f"\n╭── {header.text.strip()} ──╮")  
                    for li in ul.find_all("li"):  
                        item_text = li.text.strip()
                        current_stock.add(item_text)
                        
                        # Check if this is a new item we want to notify about
                        for notify_item in notify_items:
                            if notify_item.lower() in item_text.lower() and item_text not in previous_stock:
                                items_to_notify.append(item_text)
                        
                        # Find matching color in color_map
                        item_color = None
                        for item_name, color in color_map.items():
                            if item_name.lower() in item_text.lower():
                                item_color = color
                                break
                        
                        if item_color:
                            colored_item = colorize_text(f"│ • {item_text}", item_color)
                            print(colored_item)
                        else:
                            print(f"│ • {item_text}")
                    print("╰" + "─" * (len(header.text.strip()) + 6) + "╯")

        if not any_stock_found:
            raise Exception("No stock data found")

        # Service is back
        if service_was_down:
            send_push_notification("Grow A Garden: Service Restored", "The notifier service is now back online.")
            service_was_down = False
            last_down_notification_time = None

        # Notify new stock items
        if items_to_notify:
            for item in items_to_notify:
                send_push_notification("Grow A Garden: New Stock", f"{item} is now in stock!")

        previous_stock = current_stock

    except Exception as e:
        print(f"❌ Failed to fetch stock data: {e}")
        if not service_was_down or (last_down_notification_time is None or (datetime.now() - last_down_notification_time).total_seconds() >= 3600):
            send_push_notification("Grow A Garden: Service Down", "Notifier service is currently down or unreachable. Please use our new topic-name 'gag2-jim' to receive Grow a Garden stock and weather notifications on your phone.")
            last_down_notification_time = datetime.now()
        service_was_down = True
  
def wait_until_next_5k_plus_1():  
    now = datetime.now()  
    next_minute = (now.minute // 5) * 5 + 1  
    if now.minute % 5 >= 1:  
        next_minute += 5  
    next_time = now.replace(minute=next_minute % 60, second=0, microsecond=0)  
    if next_minute >= 60:  
        next_time += timedelta(hours=1)  
  
    while True:  
        remaining = (next_time - datetime.now()).total_seconds()  
        if remaining <= 0:  
            break  
        mins, secs = divmod(int(remaining), 60)  
        timer = f"\r⏳ Next check in {mins:02d}:{secs:02d} "  
        sys.stdout.write(timer)  
        sys.stdout.flush()  
        time.sleep(1)  
    print()  

while True:  
    scrape_stock()  
    wait_until_next_5k_plus_1()
