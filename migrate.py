import os
import shutil

IMAGE_DIR = "./images"

def get_category_folder(img_num):
    # This matches your index.html rules exactly
    if img_num == 1 or (143 <= img_num <= 147) or img_num == 175:
        return 'ram_darbar'
    elif img_num in [5, 7, 8, 10] or (12 <= img_num <= 35) or (51 <= img_num <= 64) or (149 <= img_num <= 155) or (177 <= img_num <= 180):
        return 'krishna'
    elif img_num == 2 or (36 <= img_num <= 47) or (73 <= img_num <= 88) or img_num == 148 or img_num == 188:
        return 'shiva'
    elif (68 <= img_num <= 69) or (89 <= img_num <= 93) or img_num == 172 or (181 <= img_num <= 182) or img_num == 189:
        return 'sri_ganesha'
    elif img_num in [66, 67] or (94 <= img_num <= 95) or (156 <= img_num <= 162):
        return 'vishnu'
    elif (96 <= img_num <= 103) or (166 <= img_num <= 169) or img_num == 171:
        return 'narsimha'
    elif (104 <= img_num <= 113) or (186 <= img_num <= 187):
        return 'rama'
    elif img_num in [3, 4, 6, 9, 11] or (114 <= img_num <= 119) or img_num in [173, 174, 176, 185]:
        return 'radhe_krishna'
    elif (120 <= img_num <= 129) or img_num in [134, 135, 183]:
        return 'lakshmi'
    elif (130 <= img_num <= 133) or img_num == 136 or img_num == 190:
        return 'saraswati'
    elif img_num in [50, 70] or (137 <= img_num <= 142) or img_num == 184:
        return 'hanuman'
    elif (163 <= img_num <= 165) or img_num == 170:
        return 'sai_baba'
    else:
        return 'others'

def migrate():
    if not os.path.exists(IMAGE_DIR):
        print(f"Error: {IMAGE_DIR} folder not found. Run this from your repository root.")
        return

    print("🚀 Starting image sorting based on index.html ranges...")
    moved_count = 0

    for i in range(1, 194):
        filename = f"divine_canvas_{i}.jpeg"
        source_path = os.path.join(IMAGE_DIR, filename)

        if os.path.exists(source_path):
            folder_name = get_category_folder(i)
            target_folder = os.path.join(IMAGE_DIR, folder_name)
            
            # Create subfolder if it doesn't exist
            os.makedirs(target_folder, exist_ok=True)
            
            # Move file
            shutil.move(source_path, os.path.join(target_folder, filename))
            moved_count += 1

    print(f"✅ Migration complete! Organized {moved_count} images into their respective deity folders.")

if __name__ == "__main__":
    migrate()