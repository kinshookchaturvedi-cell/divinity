import os
import json
import re
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
    folders = [f for f in os.listdir(IMAGES_DIR) if os.path.isdir(os.path.join(IMAGES_DIR, f))]
    return folders

def clean_and_parse_json(raw_text):
    """Cleans up common LLM JSON formatting errors and strips trailing commas."""
    text = raw_text.strip()
    
    # 1. Strip markdown block wraps if present
    if text.startswith("```json"):
        text = text.split("```json")[1].split("```")[0].strip()
    elif text.startswith("```"):
        text = text.split("```")[1].split("```")[0].strip()
        
    # 2. Regex to remove trailing commas before closing brackets/braces (The culprit!)
    text = re.sub(r',\s*([\]}])', r'\1', text)
    
    # 3. Attempt native loading
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 4. Emergency fallback: try extracting just everything between the first [ and last ]
        try:
            start = text.find('[')
            end = text.rfind(']') + 1
            if start != -1 and end != 0:
                fixed_text = text[start:end]
                fixed_text = re.sub(r',\s*([\]}])', r'\1', fixed_text)
                return json.loads(fixed_text)
        except Exception:
            pass
        raise

def fetch_prompts_for_deity(folder_name):
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
        "Each prompt string must specify a unique religious context, setting, and artistic style. "
        "Return ONLY a clean, valid JSON array of strings. Ensure there are no trailing commas at the end of the array items. "
        "Example format: [\"Prompt 1\", \"Prompt 2\"]"
    )
    
    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": prompt_instruction}],
        "temperature": 0.5 # Lowered temperature slightly to keep syntax strict
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        raw_content = response.json()['choices'][0]['message']['content']
        return clean_and_parse_json(raw_content)
    except Exception as e:
        print(f"❌ Failed to parse or generate prompts for {display_title}: {e}")
        return []

if __name__ == "__main__":
    deities = get_deities_from_folders()
    
    if not deities:
        print("❌ No target deity folders found. Aborting execution.")
        exit(1)
        
    print(f"Found {len(deities)} deity folders to process.\n")
    
    all_prompts = {}
    for folder in deities:
        prompts = fetch_prompts_for_deity(folder)
        if prompts:
            # Enforce exact cap of 25 if the LLM overproduced items
            all_prompts[folder] = prompts[:25]
            print(f"  ✅ Successfully loaded {len(all_prompts[folder])} prompts.")
            
    with open(OUTPUT_PROMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_prompts, f, indent=4, ensure_ascii=False)
        
    print(f"\n🎉 Prompts successfully updated and saved to: {OUTPUT_PROMPTS_FILE}")