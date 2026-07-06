import os
import json
import time
import io
import base64
import requests
from PIL import Image

# 1. Paths and Config Setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_FILE = os.path.join(SCRIPT_DIR, "generation_prompts.json")
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
DESCRIPTIONS_FILE = os.path.join(SCRIPT_DIR, "api", "descriptions.json")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "black-forest-labs/FLUX.1-schnell"  # Switches dynamically if free endpoints are routed

if not OPENROUTER_API_KEY:
    print("❌ Error: OPENROUTER_API_KEY environment variable is missing!")
    exit(1)

# 2. Safely load inputs
if not os.path.exists(PROMPTS_FILE):
    print(f"❌ Error: Cannot find prompt file at {PROMPTS_FILE}")
    exit(1)

with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
    deity_prompt_map = json.load(f)

# Load or initialize description database records
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

print(f"🚀 Initializing asset synthesis pipeline. Scanning target subdirectories...")

# 3. Processing Core Loop
for folder_name, prompts in deity_prompt_map.items():
    folder_path = os.path.join(IMAGES_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    for idx, prompt_text in enumerate(prompts, start=1):
        filename = f"divine_canvas_gen_{idx:03d}.jpeg"
        relative_registry_key = f"{folder_name}/{filename}"
        target_image_path = os.path.join(folder_path, filename)
        
        # Skip items that are already complete to save API balance quotas
        if os.path.exists(target_image_path) and relative_registry_key in descriptions_data:
            continue
            
        print(f"🎨 Synthesizing item {idx}/{len(prompts)} for deity category: {folder_name}...")
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt_text}]
                }
            ],
            "width": 1024,
            "height": 1024,
            "steps": 4
        }
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"  ❌ Generation error (Status {response.status_code}): {response.text}")
                continue
                
            response_json = response.json()
            # OpenRouter passes image output blocks inside standard chat completion message values
            raw_content = response_json['choices'][0]['message']['content']
            
            # Extract pure base64 strings if standard headers are prepended by the provider wrapper
            if "base64," in raw_content:
                raw_content = raw_content.split("base64,")[1]
                
            img_data = base64.b64decode(raw_content.strip())
            
            # 4. Processing image constraints via Pillow
            img = Image.open(io.BytesIO(img_data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Perform initial quality compress
            quality = 85
            img.save(target_image_path, "JPEG", quality=quality, optimize=True, progressive=True)
            
            # Ensure final package is under 500 KB limit
            file_size_kb = os.path.getsize(target_image_path) / 1024
            while file_size_kb > 490 and quality > 40:
                quality -= 5
                img.save(target_image_path, "JPEG", quality=quality, optimize=True)
                file_size_kb = os.path.getsize(target_image_path) / 1024
                
            # 5. Formulate short single-sentence record for descriptive dictionary metadata
            # We derive it gracefully by stripping off literal formatting references appended at the tail of prompts
            clean_desc = prompt_text.split(", in a")[0].split(", rendered in")[0].split(" style")[0]
            if not clean_desc.endswith("."):
                clean_desc += "."
                
            descriptions_data[relative_registry_key] = clean_desc
            
            # Instantly write database file state out to prevent losses during long cycles
            os.makedirs(os.path.dirname(DESCRIPTIONS_FILE), exist_ok=True)
            with open(DESCRIPTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(descriptions_data, f, indent=4, ensure_ascii=False)
                
            print(f"  ✅ Saved asset and registry info: {filename} ({file_size_kb:.1f} KB)")
            time.sleep(1.5)  # Safe delay factor for standard API tier boundaries
            
        except Exception as e:
            print(f"  ❌ Error processing pipeline step for {relative_registry_key}: {str(e)}")

print("\n🎉 Master gallery synchronization completed successfully!")