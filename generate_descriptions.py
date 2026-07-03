import os
import json
import re
from google import genai
from google.genai import types

# 1. Initialize the official Google GenAI Client
client = genai.Client()

# Path to your actual serverless API route file
JS_FILE_PATH = 'api/gallery.js' 

if not os.path.exists(JS_FILE_PATH):
    print(f"❌ Error: Could not find {JS_FILE_PATH}. Make sure you are in the root directory of your project.")
    exit(1)

# Read the existing JavaScript file content
with open(JS_FILE_PATH, 'r', encoding='utf-8') as f:
    js_content = f.read()

# 2. Use Regex to extract the raw JSON object from the 'const galleryData = { ... };' block
json_match = re.search(r'const\s+galleryData\s*=\s*(\{.*?\});', js_content, re.DOTALL)
if not json_match:
    print("❌ Error: Could not find the 'galleryData' object variable inside api/gallery.js")
    exit(1)

gallery_data_str = json_match.group(1)
gallery_data = json.loads(gallery_data_str)

print("✨ Initiating computer vision analysis for Divine Canvas assets...")

# 3. Walk through each category and image asset
for category_key, category_data in gallery_data.items():
    if category_key == "ALL": 
        continue
        
    folder_name = category_data.get('folder')
    title = category_data.get('title')
    
    for img_obj in category_data.get('images', []):
        filename = img_obj.get('filename')
        image_path = os.path.join('images', folder_name, filename)
        
        if not os.path.exists(image_path):
            print(f"⚠️ Skipping missing file: {image_path}")
            continue
            
        print(f"📸 Analyzing {filename} under {title}...")
        
        try:
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
                
            # Call the vision model to overwrite the description
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg'
                    ),
                    f"Provide a short, elegant, one-sentence spiritual and poetic description for this artwork of {title}. Do not include quotes or filler text."
                ]
            )
            
            img_obj['description'] = response.text.strip()
            print(f"✅ Success: \"{img_obj['description']}\"")
            
        except Exception as e:
            print(f"❌ Failed to analyze {filename}: {str(e)}")

# 4. Convert the updated data back into formatted JSON and replace it inside api/gallery.js
updated_json_str = json.dumps(gallery_data, indent=4)
updated_js_content = re.sub(
    r'const\s+galleryData\s*=\s*\{.*?\};', 
    f'const galleryData = {updated_json_str};', 
    js_content, 
    flags=re.DOTALL
)

with open(JS_FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(updated_js_content)

print("\n🎉 api/gallery.js has been beautifully updated with computer vision one-liners!")