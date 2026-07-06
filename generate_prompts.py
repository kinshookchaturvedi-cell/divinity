import os
import json
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY_HERE")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Dynamically resolve paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, 'images')
OUTPUT_PROMPTS_FILE = os.path.join(SCRIPT_DIR, 'generation_prompts.json')

def get_deities_from_folders():
    """Dynamically scan the images folder to determine the list of deities."""
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ Error: Cannot find images directory at absolute path: {IMAGES_DIR}")
        return []
        
    # Gather only directory names, ignoring hidden system files like .DS_Store
    folders = [f for f in os.listdir(IMAGES_DIR) if os.path.isdir(os.path.join(IMAGES_DIR, f))]
    return folders

def fetch_prompts_for_deity(folder_name):
    # Clean up directory names for the AI director's contextual understanding
    display_title = folder_name.replace('_', ' ').title()
    if "Sai Baba" in display_title:
        display_title = "Sai Baba"
    elif "Narsimha" in display_title:
        display_title = "Lord Narasimha"
        
    print(f"🧠 Brainstorming 25 unique art prompts for {display_title} via OpenRouter...")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt_instruction = (
        f"Act as an art director. Generate exactly 25 highly diverse, single-sentence image generation prompts for artwork depicting {display_title}. "
        "Each prompt must specify a different religious context, setting (e.g., ancient temples, cosmic spaces, serene nature), lighting condition, and artistic style (e.g., oil painting, digital art, traditional fresco). "
        "Return ONLY a valid JSON array of strings. Do not include markdown blocks, introductory text, or numbers."
    )
    
    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": prompt_instruction}],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        text = response.json()['choices'][0]['message']['content'].strip()
        
        # Strip away unexpected markdown wrapper leaks from the response data
        if text.startswith("```json"):
            text = text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("```"):
            text = text.split("```")[1].split("```")[0].strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"❌ Failed to generate prompts for {display_title}: {e}")
        return []

if __name__ == "__main__":
    deities = get_deities_from_folders()
    
    if not deities:
        print("❌ No target deity folders found. Aborting execution.")
        exit(1)
        
    print(f"Found {len(deities)} deity folders to process: {deities}\n")
    
    all_prompts = {}
    for folder in deities:
        prompts = fetch_prompts_for_deity(folder)
        if prompts:
            all_prompts[folder] = prompts
            
    with open(OUTPUT_PROMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_prompts, f, indent=4, ensure_ascii=False)
        
    print(f"\n🎉 Prompts successfully updated and saved to: {OUTPUT_PROMPTS_FILE}")