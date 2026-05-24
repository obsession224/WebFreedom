import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote

# Источники подписок
SOURCES = [
    "https://sub.harknmav.fun/mendc2yGo4ELy19a"
]

OUTPUT_FILE = "webfreedom_rg_only.txt"
NEW_NAME = "Tg only t.me/webfreedomvpn"  # Исправлено: теперь такое же как в рабочем коде

# Дополнительные настройки из рабочего кода
HEADER_COMMENT = "//profile-title: t.me/webfreedomvpn"

def process_config_line(line, new_name):
    """Обрабатывает строку конфига, меняет название"""
    line = line.strip()
    
    if not line.startswith("vless://"):
        return None
    
    # Меняем название после #
    if "#" in line:
        base = line.split("#")[0]
    else:
        base = line
    
    # Проверяем, нужно ли переименовывать (как в рабочем коде)
    original_name = ""
    if "#" in line:
        original_name = line.split("#")[1]
    
    # Если есть кириллица или @ - переименовываем
    import re
    cyrillic_pattern = re.compile(r"[а-яА-ЯёЁ]")
    
    need_rename = (
        "@" in original_name or
        cyrillic_pattern.search(original_name) or
        "бот" in original_name.lower() or
        "fastcon" in original_name.lower() or
        "безлимит" in original_name.lower()
    )
    
    if need_rename or new_name:
        final_name = new_name
    else:
        final_name = original_name
    
    new_line = f"{base}#{quote(final_name)}"
    return new_line

configs = []
total_parsed = 0

for url in SOURCES:
    try:
        text = requests.get(url, timeout=20).text
        
        # Проверяем, не закодирован ли ответ в base64 (как в рабочем коде)
        if not text.startswith("vless://"):
            try:
                import base64
                missing_padding = len(text) % 4
                if missing_padding:
                    text += '=' * (4 - missing_padding)
                decoded = base64.b64decode(text).decode("utf-8", errors="ignore")
                if decoded.startswith("vless://"):
                    text = decoded
            except:
                pass
        
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("vless://"):
                continue
            
            total_parsed += 1
            processed = process_config_line(line, NEW_NAME)
            if processed:
                configs.append(processed)
        
        print(f"[OK] Parsed: {url}")

    except Exception as e:
        print(f"[ERROR] {url} -> {e}")

# Удаляем полные дубликаты
configs = list(dict.fromkeys(configs))

# Добавляем заголовок с именем подписки (как в рабочем коде)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(HEADER_COMMENT + "\n")
    f.write("\n".join(configs))

print(f"[DONE] Saved {len(configs)} configs.")
print(f"[INFO] Total parsed: {total_parsed}")
print(f"[INFO] Subscription name: {NEW_NAME}")
