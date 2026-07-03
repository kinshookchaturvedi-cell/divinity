import os
import json
from google import genai
from google.genai import types

# 1. Initialize the official Google GenAI Client
# Make sure you run 'export GEMINI_API_KEY="your-key-here"' in your terminal first
client = genai.Client()

# 2. Path to your gallery registry JSON (adjust if it's directly inside api/gallery.js)
DATA_FILE_PATH = 'api/gallery_data.json' 

with open(DATA_FILE_PATH, 'r') as f:
    gallery_data = json.load(f)

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
            # Load the binary image data
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()
                
            # Call the vision model to overwrite the description
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg' # Adjust to image/png if you use PNGs
                    ),
                    f"Provide a short, elegant, one-sentence spiritual and poetic description for this artwork of {title}. Do not include quotes or filler text."
                ]
            )
            
            # OVERWRITE step: Apply the newly generated vision description
            img_obj['description'] = response.text.strip()
            print(f"✅ Success: \"{img_obj['description']}\"")
            
        except Exception as e:
            print(f"❌ Failed to analyze {filename}: {str(e)}")

# 4. Save the updated configuration map back to your registry file
with open(DATA_FILE_PATH, 'w') as f:
    json.dump(gallery_data, f, indent=4)

print("\n🎉 All descriptions have been overwritten successfully by Computer Vision!")