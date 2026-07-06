import os
import json
import time
import base64
import requests

# 1. Dynamically find the absolute path of this script's folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, 'images')
OUTPUT_JSON = os.path.join(SCRIPT_DIR, 'api', 'descriptions.json')

# 2. OpenRouter Configuration
# Make sure to set your token in your terminal env: export OPENROUTER_API_KEY="your-key"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Choose your vision model from OpenRouter (e.g., google/gemini-2.5-flash, meta-llama/llama-3.2-11b-vision-instruct)
MODEL_NAME = "google/gemini-2.5-flash" 

if not os.path.exists(IMAGES_DIR):
    print(f"❌ Error: Cannot find images directory at absolute path: {IMAGES_DIR}")
    exit(1)

os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

# 3. Read existing records to prevent duplicate execution spending
descriptions_registry = {}
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
        try:
            descriptions_registry = json.load(f)
            print(f"Loaded {len(descriptions_registry)} existing image entries.")
        except Exception:
            pass

print(f"✨ Running OpenRouter Vision Processing using model: {MODEL_NAME}...")

folders = [f for f in os.listdir(IMAGES_DIR) if os.path.isdir(os.path.join(IMAGES_DIR, f))]

for folder in folders:
    folder_path = os.path.join(IMAGES_DIR, folder)
    
    display_title = folder.replace('_', ' ').title()
    if "Sri Ganesha" in display_title:
        display_title = "Ganesha"
    if "Radhe Krishna" in display_title:
        display_title = "Radhe"
        
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    
    for filename in files:
        registry_key = f"{folder}/{filename}"
        image_path = os.path.join(folder_path, filename)
        
        if registry_key in descriptions_registry and descriptions_registry[registry_key]:
            continue
            
        print(f"📸 OpenRouter analyzing: {registry_key}...")
        
        try:
            # Read image and convert to Base64 data string
            with open(image_path, 'rb') as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Construct standard multimodal schema payload
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Provide a short, elegant, one-sentence spiritual description for this artwork of {display_title}. No quotes."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 30,
                "temperature": 0.4
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code == 200:
                ai_text = response_data['choices'][0]['message']['content'].strip()
                descriptions_registry[registry_key] = ai_text
                print(f"  ✅ Success -> \"{ai_text}\"")
                
                # Save data state immediately
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(descriptions_registry, f, indent=4, ensure_ascii=False)
                    f.flush()
                
                # ⏳ Tiny fraction-of-a-second breathing room (No more 4 or 35 second long blocks!)
                time.sleep(0.5)
            else:
                print(f"  ❌ OpenRouter API Error ({response.status_code}): {response.text}")
                if response.status_code == 429:
                    print("  ⏳ OpenRouter rate limits hit. Pausing 10s...")
                    time.sleep(10)
                    
        except Exception as e:
            print(f"  ❌ Processing script block fault for {filename}: {str(e)}")

print(f"\n🎉 Process Finished! Verified target file location: {OUTPUT_JSON}")