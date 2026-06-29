import os
import time
import requests

IMAGE_DIR = "./mock_images"

# 1. Broad deity queries optimized for Wikipedia's media engine
DEITY_QUERIES = {
    "ram_darbar": "Rama_darbar",
    "krishna": "Krishna",
    "shiva": "Shiva",
    "sri_ganesha": "Ganesha",
    "vishnu": "Vishnu",
    "narsimha": "Narasimha",
    "rama": "Rama",
    "radhe_krishna": "Radha_Krishna",
    "lakshmi": "Lakshmi",
    "saraswati": "Saraswati",
    "hanuman": "Hanuman",
    "sai_baba": "Sai_Baba_of_Shirdi",
    "durga": "Durga"
}

IMAGES_PER_DEITY = 100

def get_wikimedia_images(query, limit):
    """Fetches real image URLs directly from Wikimedia Commons matching the deity."""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6,  # Namespace 6 is strictly for Media/Images
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url"
    }
    
    headers = {"User-Agent": "DivinityGalleryBot/1.0 (contact: admin@example.com)"}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        if response.status_code != 200:
            return []
        
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        
        urls = []
        for page_id, page_info in pages.items():
            img_info = page_info.get("imageinfo", [{}])[0]
            img_url = img_info.get("url")
            if img_url:
                urls.append(img_url)
        return urls
    except Exception as e:
        print(f"   ⚠️ Wikipedia API error: {e}")
        return []

def populate_relevant_assets():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    print("🚀 Starting real-time deity image collection via Wikimedia Commons...\n")

    for deity, query in DEITY_QUERIES.items():
        folder_path = os.path.join(IMAGE_DIR, deity)
        os.makedirs(folder_path, exist_ok=True)
        print(f"📁 Processing folder: {deity}")

        # Fetch a pool of matching URLs
        img_urls = get_wikimedia_images(query, IMAGES_PER_DEITY)
        
        if not img_urls:
            print(f"   ⚠️ Could not find specific media pool for {deity}. Skipping.")
            continue

        for i, img_url in enumerate(img_urls, start=1):
            file_name = f"mock_artwork_{i}.jpg"
            target_file_path = os.path.join(folder_path, file_name)

            if os.path.exists(target_file_path):
                continue

            try:
                # Download the actual historical/spiritual image
                img_response = requests.get(img_url, timeout=15)
                if img_response.status_code == 200:
                    with open(target_file_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"   ↳ [Success] Saved {i}/{len(img_urls)} -> {file_name}")
                else:
                    print(f"   ❌ Failed to download asset index {i}")
                
                time.sleep(0.2)  # Polite crawling buffer
            except Exception as e:
                print(f"   ❌ Error saving file {i}: {e}")

if __name__ == "__main__":
    populate_relevant_assets()