import os
import re

ROOT_DIR = '.'
BASE_LANG = 'com_gridbox_en-GB'

def parse_ini_file(file_path):
    keys = {}
    order = []
    if not os.path.exists(file_path):
        return keys, order
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith(';'):
                continue
            match = re.match(r'^([A-Z0-9_-]+)\s*=\s*(["\']?)(.*?)\2$', stripped)
            if match:
                key, _, value = match.groups()
                keys[key] = value
                if key not in order:
                    order.append(key)
    return keys, order

def save_ini_file(file_path, keys, order):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for key in order:
            val = keys.get(key, '')
            f.write(f'{key}="{val}"\n')

def sync_language_files():
    base_dir = os.path.join(ROOT_DIR, BASE_LANG)
    if not os.path.exists(base_dir):
        print(f"Base language folder {BASE_LANG} not found!")
        return

    base_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.ini'):
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                base_files.append(rel_path)

    for item in os.listdir(ROOT_DIR):
        lang_dir = os.path.join(ROOT_DIR, item)
        if not os.path.isdir(lang_dir) or item == BASE_LANG or not item.startswith('com_gridbox_'):
            continue
            
        print(f"Synchronizing structure for: {item}")
        
        for rel_path in base_files:
            base_file_path = os.path.join(base_dir, rel_path)
            target_file_path = os.path.join(lang_dir, rel_path)
            
            base_keys, base_order = parse_ini_file(base_file_path)
            target_keys, _ = parse_ini_file(target_file_path)
            
            merged_keys = {}
            for key in base_order:
                en_val = base_keys.get(key, '')
                if key in target_keys and target_keys[key].strip() != '' and target_keys[key] != en_val:
                    merged_keys[key] = target_keys[key]
                else:
                    merged_keys[key] = en_val
            
            translated_keys = [k for k in base_order if merged_keys.get(k, '') != base_keys.get(k, '')]
            untranslated_keys = [k for k in base_order if merged_keys.get(k, '') == base_keys.get(k, '')]
            
            translated_keys.sort()
            untranslated_keys.sort()
            
            final_order = translated_keys + untranslated_keys
            
            save_ini_file(target_file_path, merged_keys, final_order)

if __name__ == '__main__':
    sync_language_files()
    print("Sync and sorting completed successfully!")
