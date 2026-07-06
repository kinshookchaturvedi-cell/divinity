import os
import json
import time
from google import genai
from google.genai import types

# 1. Dynamically find the absolute path of this script's folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, 'images')
OUTPUT_JSON = os.path.join(SCRIPT_DIR, 'api', 'descriptions.json')

# Initialize the official Google GenAI Client
client = genai.Client()

if not os.path.exists(IMAGES_DIR):
    print(f"❌ Error: Cannot find images directory at absolute path: {IMAGES_DIR}")
    exit(1)

# Ensure the api/ directory exists absolutely
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

# 2. Read existing database records to avoid duplicate API usage bills
descriptions_registry = {}
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
        try:
            descriptions_registry = json.load(f)
            print(f"Loaded {len(descriptions_registry)} existing image entries from database.")
        except Exception:
            pass

print("✨ Running Optimized Computer Vision Analysis on local image assets...")

# 3. Gather exactly the folders present in your directory structure
folders = [f for f in os.listdir(IMAGES_DIR) if os.path.isdir(os.path.join(IMAGES_DIR, f))]

for folder in folders:
    folder_path = os.path.join(IMAGES_DIR, folder)
    
    # Format the display title clean
    display_title = folder.replace('_', ' ').title()
    if "Sri Ganesha" in display_title:
        display_title = "Ganesha"
    if "Radhe Krishna" in display_title:
        display_title = "Radhe"
        
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    
    for filename in files:
        registry_key = f"{folder}/{filename}"
        image_path = os.path.join(folder_path, filename)
        
        # Skip if we already have this image analyzed successfully
        if registry_key in descriptions_registry and descriptions_registry[registry_key]:
            continue
            
        print(f"📸 Gemini Vision analyzing: {registry_key}...")
        
        try:
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
                
            # Request description with highly optimized configuration rules
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite', # 💡 Use lite model for heavy bulk processing
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                    f"Provide a short, elegant, one-sentence spiritual description for this artwork of {display_title}. No quotes."
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=30,  # 💡 Caps response size to save output token cost
                    temperature=0.4        # Keeps the responses concise and focused
                )
            )
            
            ai_text = response.text.strip()
            descriptions_registry[registry_key] = ai_text
            print(f"  ✅ Success -> \"{ai_text}\"")
            
            # Save progress immediately
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(descriptions_registry, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
                
            # ⏳ Safe, steady pacing to protect your free-tier vision quota
            time.sleep(4.0)
            
        except Exception as e:
            print(f"  ❌ API failure or write block for {filename}: {str(e)}")
            
            # 🛑 Emergency backup: if a rate limit is still triggered, sit tight
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"  ⏳ Quota window full. Pausing for 35 seconds to let the rate limit clear...")
                time.sleep(60)

print(f"\n🎉 Process Finished! Verified target file location: {OUTPUT_JSON}")
print(f"Total structured descriptions successfully embedded: {len(descriptions_registry)}")