import os
import time
import requests

IMAGE_DIR = "./mock_images"

# Broad deity queries optimized for Wikimedia's media engine
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

# Comprehensive headers to thoroughly mimic a standard web browser connection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

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
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        
        # If the search endpoint itself throttles us, pause gracefully
        if response.status_code == 429:
            print("   ⚠️ Search API throttled (429). Waiting 10 seconds to cool down...")
            time.sleep(10)
            response = requests.get(url, params=params, headers=HEADERS, timeout=15)

        if response.status_code != 200:
            print(f"   ❌ Search failure status code: {response.status_code}")
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
            time.sleep(2)  # Cooldown before hitting next category search
            continue

        for i, img_url in enumerate(img_urls, start=1):
            file_name = f"mock_artwork_{i}.jpg"
            target_file_path = os.path.join(folder_path, file_name)

            if os.path.exists(target_file_path):
                continue

            # Adaptive download mechanism with retry system for individual image CDNs
            retries = 3
            backoff = 5
            
            while retries > 0:
                try:
                    img_response = requests.get(img_url, headers=HEADERS, timeout=15)
                    
                    if img_response.status_code == 200:
                        with open(target_file_path, 'wb') as f:
                            f.write(img_response.content)
                        print(f"   ↳ [Success] Saved {i}/{len(img_urls)} -> {file_name}")
                        break
                    elif img_response.status_code == 429:
                        print(f"   ⚠️ Download Throttled (429). Retrying in {backoff}s...")
                        time.sleep(backoff)
                        backoff *= 2
                        retries -= 1
                    else:
                        print(f"   ❌ Failed asset index {i} (Status: {img_response.status_code})")
                        break
                except KeyboardInterrupt:
                    print("\n🛑 Execution paused by user. Stopping safely...")
                    return
                except Exception as e:
                    print(f"   ❌ Error saving file {i}: {e}")
                    time.sleep(1)
                    break
            
            # Gentle pacing interval between downloads
            time.sleep(0.5)
            
        # Clear breather delay after finishing a complete deity sequence
        print(f"✅ Finished {deity}. Resting engine...")
        time.sleep(3)

if __name__ == "__main__":
    populate_relevant_assets()