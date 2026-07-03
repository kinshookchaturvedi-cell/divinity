import os
import json
from google import genai
from google.genai import types

# 1. Initialize the official Google GenAI Client
client = genai.Client()

IMAGES_DIR = 'images'
OUTPUT_JSON = os.path.join('api', 'descriptions.json')

if not os.path.exists(IMAGES_DIR):
    print(f"❌ Error: Could not find '{IMAGES_DIR}' directory. Ensure you run this from the project root.")
    exit(1)

os.makedirs('api', exist_ok=True)

# Load existing descriptions if file exists, to avoid re-running things we already paid API credits for
descriptions_registry = {}
if os.path.exists(OUTPUT_JSON):
    with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
        try:
            descriptions_registry = json.load(f)
        except json.JSONDecodeError:
            pass

print("✨ Running Computer Vision Analysis on local image folders...")

# 2. Iterate through folders and files locally
for folder in os.listdir(IMAGES_DIR):
    folder_path = os.path.join(IMAGES_DIR, folder)
    if not os.path.isdir(folder_path):
        continue
        
    # Format a display title similar to how your JS file does it
    display_title = folder.replace('_', ' ').title()
    if "Sri Ganesha" in display_title: display_title = "Ganesha"
    if "Radhe Krishna" in display_title: display_title = "Radhe"
    
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            continue
            
        # Create a unique key using the folder and file combination
        registry_key = f"{folder}/{filename}"
        
        # Skip if we already have it generated
        if registry_key in descriptions_registry and descriptions_registry[registry_key]:
            print(f"⏭️ Skipping (already indexed): {registry_key}")
            continue
            
        image_path = os.path.join(folder_path, filename)
        print(f"📸 Analyzing image contents via Gemini Vision: {registry_key}...")
        
        try:
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
                
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                    f"Provide a short, elegant, one-sentence spiritual and poetic description for this artwork of {display_title}. Do not use quotes or introductory filler text."
                ]
            )
            
            descriptions_registry[registry_key] = response.text.strip()
            print(f"✅ Success: \"{descriptions_registry[registry_key]}\"")
            
            # Save incrementally after each successful run
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(descriptions_registry, f, indent=4, ensure_with_ascii=False)
                
        except Exception as e:
            print(f"❌ Failed to analyze {filename}: {str(e)}")

print(f"\n🎉 Description dataset built successfully and stored at {OUTPUT_JSON}!")