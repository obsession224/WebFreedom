import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote

# Источники подписок
SOURCES = [
    "https://sub.harknmav.fun/mendc2yGo4ELy19a"
]

OUTPUT_FILE = "webfreedom_rg_only.txt"

NEW_NAME = "WebFreedom tg only"

configs = []

for url in SOURCES:
    try:
        text = requests.get(url, timeout=20).text

        for line in text.splitlines():
            line = line.strip()

            if not line.startswith("vless://"):
                continue

            # Меняем название после #
            if "#" in line:
                base = line.split("#")[0]
            else:
                base = line

            new_line = f"{base}#{quote(NEW_NAME)}"

            configs.append(new_line)

        print(f"[OK] Parsed: {url}")

    except Exception as e:
        print(f"[ERROR] {url} -> {e}")

# Удаляем полные дубликаты
configs = list(dict.fromkeys(configs))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(configs))

print(f"[DONE] Saved {len(configs)} configs.")
