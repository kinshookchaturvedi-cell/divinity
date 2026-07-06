import os
import json
import time
import io
import base64
import requests
from PIL import Image

# --- SAFETY SETTING ---
SANDBOX_MODE = True  # Set to False when you are ready to generate all 25 images per deity!

# 1. Paths and Config Setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_FILE = os.path.join(SCRIPT_DIR, "generation_prompts.json")
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
DESCRIPTIONS_FILE = os.path.join(SCRIPT_DIR, "api", "descriptions.json")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Official OpenRouter Dedicated Image Generation Route
API_URL = "https://openrouter.ai/api/v1/images/generations"
MODEL_NAME = "black-forest-labs/flux.2-klein-4b:free" 

if not OPENROUTER_API_KEY:
    print("❌ Error: OPENROUTER_API_KEY environment variable is missing!")
    exit(1)

if not os.path.exists(PROMPTS_FILE):
    print(f"❌ Error: Cannot find prompt file at {PROMPTS_FILE}")
    exit(1)

with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
    deity_prompt_map = json.load(f)

descriptions_data = {}
if os.path.exists(DESCRIPTIONS_FILE):
    try:
        with open(DESCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            descriptions_data = json.load(f)
    except Exception:
        descriptions_data = {}

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/kinshookchaturvedi-cell/divinity",
    "X-Title": "Divine Canvas Master Pipeline"
}

print(f"🚀 Initializing asset synthesis pipeline via Flux 2 Klein. Sandbox Mode: {SANDBOX_MODE}")

# 2. Processing Core Loop
for folder_name, prompts in deity_prompt_map.items():
    folder_path = os.path.join(IMAGES_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    for idx, prompt_text in enumerate(prompts, start=1):
        filename = f"divine_canvas_gen_{idx:03d}.jpeg"
        relative_registry_key = f"{folder_name}/{filename}"
        target_image_path = os.path.join(folder_path, filename)
        
        if os.path.exists(target_image_path) and relative_registry_key in descriptions_data:
            continue
            
        print(f"🎨 Synthesizing item {idx}/{len(prompts)} for deity category: {folder_name}...")
        
        # Standard payload configuration parameters for OpenRouter Dedicated Images API
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt_text,
            "aspect_ratio": "1:1",
            "output_format": "jpeg"
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"  ❌ Generation error (Status {response.status_code}): {response.text}")
                continue
                
            response_json = response.json()
            
            # OpenRouter dedicated image API returns structural mappings in an array under 'data'
            if 'data' not in response_json or not response_json['data']:
                print(f"  ❌ Malformed response payload received: {response_json}")
                continue
                
            image_data_block = response_json['data'][0]
            img_data = None
            
            # Gracefully handle inline base64 string or target response URL
            if 'b64_json' in image_data_block:
                raw_content = image_data_block['b64_json']
                if "base64," in raw_content:
                    raw_content = raw_content.split("base64,")[1]
                img_data = base64.b64decode(raw_content.strip())
            elif 'url' in image_data_block:
                img_url = image_data_block['url']
                print(f"  🔗 Pulling remote image asset from provider CDN: {img_url}")
                img_data = requests.get(img_url, timeout=30).content
                
            if not img_data:
                print("  ❌ Error: Image parsing block failed to resolve data assets.")
                continue

            # 3. Post-Processing: Convert and Compress to .jpeg
            img = Image.open(io.BytesIO(img_data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Initial optimization savings step
            quality = 85
            img.save(target_image_path, "JPEG", quality=quality, optimize=True, progressive=True)
            file_size_kb = os.path.getsize(target_image_path) / 1024
            
            # Bound loop safety protection targeting sub-500 KB limits
            while file_size_kb > 490 and quality > 40:
                quality -= 5
                img.save(target_image_path, "JPEG", quality=quality, optimize=True)
                file_size_kb = os.path.getsize(target_image_path) / 1024
                
            # 4. Formulate short description metadata
            clean_desc = prompt_text.split(", in a")[0].split(", rendered in")[0].split(" style")[0]
            if not clean_desc.endswith("."):
                clean_desc += "."
                
            descriptions_data[relative_registry_key] = clean_desc
            
            # Save metadata updates to api/descriptions.json
            os.makedirs(os.path.dirname(DESCRIPTIONS_FILE), exist_ok=True)
            with open(DESCRIPTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(descriptions_data, f, indent=4, ensure_ascii=False)
                
            print(f"  ✅ Saved asset: {filename} ({file_size_kb:.1f} KB at Quality {quality})")
            
            if SANDBOX_MODE:
                print("\n🛑 Sandbox test run successful! Turning off script execution safely.")
                exit(0)
                
            time.sleep(1.5)
            
        except Exception as e:
            print(f"  ❌ Error processing pipeline step for {relative_registry_key}: {str(e)}")

print("\n🎉 Master gallery synchronization completed successfully!")