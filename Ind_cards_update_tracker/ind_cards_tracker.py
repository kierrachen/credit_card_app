import requests
from bs4 import BeautifulSoup
import hashlib
import json
import time
import csv


cardcsv = "C:/Users/yanmi/credit_card_app/assets/credit_cards_clean_v3.csv"
# cardcsv = "C:/Users/yanmi/credit_card_app/assets/Cardnewroom.csv"

AMEX_CARDS = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CreditCardUpdateChecker/1.0)"
}

HASH_FILE = "amex_card_hashes.json"

def parse_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            card = row["Card"]
            AMEX_CARDS[card] = row["Apply"]

def extract_relevant_text(soup):
    sections = []

    # Common AmEx section tags (they reuse patterns)
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if any(keyword in text.lower() for keyword in [
            "bonus", "annual fee", "membership rewards",
            "cash back", "points", "terms", "reward", "miles", "benefit"
        ]):
            sections.append(text)

    return " ".join(sections)


def fetch_card_content(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return extract_relevant_text(soup)


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_previous_hashes():
    try:
        with open(HASH_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_hashes(hashes):
    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f, indent=2)


def check_amex_updates():
    previous = load_previous_hashes()
    current = {}

    parse_csv(cardcsv)

    i = 0
    for card, url in AMEX_CARDS.items():
        i = i + 1
        print(f"{i}  Checking {card}...   ", end="")
        try:
            content = fetch_card_content(url)
            content_hash = hash_text(content)
            current[card] = content_hash

            if card in previous:
                if previous[card] != content_hash:
                    print(f"⚠️  Update detected for {card}")
                else:
                    print(f"✓ No change")
            else:
                print("✓ Tracking for first time")

            time.sleep(6)  # very important for AmEx
        except Exception as e:
            print(f"❌ Error checking {card}: {e}")

    save_hashes(current)


if __name__ == "__main__":
    check_amex_updates()
