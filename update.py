import requests
from urllib.parse import quote

SOURCES = ["https://sub.harknmav.fun/mendc2yGo4ELy19a"]
OUTPUT_FILE = "webfreedom_rg_only.txt"
NEW_NAME = "t.me/webfreedomvpn"

def process_line(line):
    line = line.strip()
    if not line.startswith("vless://"):
        return None
    base = line.split("#")[0] if "#" in line else line
    return f"{base}#{quote(NEW_NAME)}"

all_configs = []
for url in SOURCES:
    try:
        resp = requests.get(url, timeout=20)
        raw = resp.text
        # Декодируем Base64, если нужно
        if not raw.startswith("vless://"):
            import base64
            try:
                raw = base64.b64decode(raw).decode()
            except:
                pass
        for line in raw.splitlines():
            cfg = process_line(line)
            if cfg:
                all_configs.append(cfg)
        print(f"OK: {url} -> {len(all_configs)} configs so far")
    except Exception as e:
        print(f"ERROR {url}: {e}")

all_configs = list(dict.fromkeys(all_configs))  # удалить дубликаты

# Записываем файл
with open(OUTPUT_FILE, "w") as f:
    f.write("\n".join(all_configs))

print(f"Saved {len(all_configs)} configs to {OUTPUT_FILE}")

# Доп. проверка: прочитаем и выведем первые 3 строки
with open(OUTPUT_FILE, "r") as f:
    first_lines = f.readlines()[:3]
    print("First lines of output file:")
    for line in first_lines:
        print(line.strip()[:80])
