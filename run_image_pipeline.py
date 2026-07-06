# --- FIX: Change the URL from /images/generations to the standard completions route ---
        try:
            # OpenRouter routes image models natively through the main completions endpoint
            img_gen_url = "https://openrouter.ai/api/v1/chat/completions"
            
            # Correct payload format for OpenRouter multimodal image endpoints
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_text
                            }
                        ]
                    }
                ],
                # Pass sizing hints directly inside the standard payload parameters
                "width": 1024,
                "height": 1024,
                "steps": 4
            }
            
            response = requests.post(img_gen_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"  ❌ Generation error (Status {response.status_code}): {response.text}")
                continue
                
            response_json = response.json()
            
            # OpenRouter passes image output blocks inside standard chat completion content strings
            raw_content = response_json['choices'][0]['message']['content']