import os
import re
import urllib.request
import urllib.parse
import json
import time

MASTER_LANG = 'com_gridbox_en-GB'
ROOT_DIR = '.' 

def translate_text(text, target_lang):
    if not text.strip():
        return ""
    
    lang_code = target_lang.split('-')[0]
    
    url = "https://api.mymemory.translated.net/get?q=" + urllib.parse.quote(text) + "&langpair=en|" + lang_code
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    for attempt in range(3):
        try:
            time.sleep(0.6)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and 'responseData' in data and data['responseData']['translatedText']:
                    translated = data['responseData']['translatedText']
                    if not translated.startswith("MYMEMORY WARNING") and not translated.startswith("QUERY LENGTH"):
                        return translated
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"Rate limit (429) hit for '{text}'. Waiting before retry...")
                time.sleep(5 * (attempt + 1))
            else:
                print(f"HTTP error for '{text}': {e}")
                break
        except Exception as e:
            print(f"Translation error for '{text}': {e}")
            break
            
    return text

def parse_ini(filepath):
    keys = {}
    order = []
    other_lines = []
    
    if not os.path.exists(filepath):
        return keys, order, other_lines
    
    with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        for line in f:
            match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*"(.*)"', line.strip())
            if match:
                key, val = match.groups()
                keys[key] = val
                if key not in order:
                    order.append(key)
            else:
                other_lines.append(line)
                
    return keys, order, other_lines

def sync_translations():
    master_path = os.path.join(ROOT_DIR, MASTER_LANG)
    if not os.path.exists(master_path):
        print(f"Master language folder {MASTER_LANG} not found!")
        return

    master_files = []
    for root, _, files in os.walk(master_path):
        for file in files:
            if file.endswith('.ini'):
                rel_path = os.path.relpath(os.path.join(root, file), master_path)
                master_files.append(rel_path)

    for rel_path in master_files:
