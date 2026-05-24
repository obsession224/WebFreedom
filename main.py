import json
import base64
import re
import urllib.parse
import requests

# --- НАСТРОЙКИ ФИЛЬТРАЦИИ И ИМЕН ---
CYRILLIC_PATTERN = re.compile(r"[а-яА-ЯёЁ]")
VALID_PROTOCOLS = ("vless://", "vmess://", "trojan://", "ss://")

# Словарь для поиска стран в названиях
COUNTRY_FLAGS = {
    "ru": "🇷🇺", "russia": "🇷🇺", "россия": "🇷🇺",
    "us": "🇺🇸", "usa": "🇺🇸", "сша": "🇺🇸", "america": "🇺🇸",
    "de": "🇩🇪", "germany": "🇩🇪", "германия": "🇩🇪",
    "nl": "🇳🇱", "netherlands": "🇳🇱", "нидерланды": "🇳🇱",
    "fi": "🇫🇮", "finland": "🇫🇮", "финляндия": "🇫🇮",
    "pl": "🇵🇱", "poland": "🇵🇱", "польша": "🇵🇱",
    "kz": "🇰🇿", "kazakhstan": "🇰🇿", "казахстан": "🇰🇿",
    "fr": "🇫🇷", "france": "🇫🇷", "франция": "🇫🇷",
    "gb": "🇬🇧", "uk": "🇬🇧", "великобритания": "🇬🇧",
}


def extract_urls_from_karing(file_path="karing_subscribe.json"):
    """Автоматически парсит и собирает все HTTP ссылки из файла Karing."""
    print(f"📦 Читаю настройки из {file_path}...")
    urls = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("items", []):
            url = item.get("urlOrPath", "").strip()
            if url.startswith("http"):
                urls.append(url)
        print(f"✅ Найдено динамических ссылок подписок: {len(urls)}")
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл {file_path} не найден!")
    except Exception as e:
        print(f"❌ Ошибка при чтении конфигурации Karing: {e}")
    return urls


def detect_flag(name):
    """Определяет эмодзи-флаг страны по текстовым вхождениям."""
    name_lower = name.lower()

    # Сначала проверяем, есть ли уже юникод-эмодзи флаг в имени
    flags = re.findall(r"[\U0001F1E6-\U0001F1FF]{2}", name)
    if flags:
        return flags[0]

    # Ищем ключевые слова стран
    words = re.findall(r"[a-zа-яё]+", name_lower)
    for word in words:
        if word in COUNTRY_FLAGS:
            return COUNTRY_FLAGS[word]
    return "🌐"


def process_and_rename(line):
    """Разбирает и брендирует строку конфига. Рекламу возвращает как None."""
    if "#" not in line:
        return None

    base_part, original_name = line.split("#", 1)
    name_decoded = urllib.parse.unquote(original_name).strip()

    # СВЕРХ-ЖЕСТКИЙ ФИЛЬТР СПАМА
    hard_spam_words = ["оформи vip", "купить vip", "рублей в месяц", "руб/мес", "цена:", "shop", "купи vpn"]
    if any(spam in name_decoded.lower() for spam in hard_spam_words):
        return None

    # ПРАВИЛО ПЕРЕИМЕНОВАНИЯ
    need_rename = (
            "@" in name_decoded
            or CYRILLIC_PATTERN.search(name_decoded)
            or "бот" in name_decoded.lower()
            or "fastcon" in name_decoded.lower()
            or "безлимит" in name_decoded.lower()
    )

    if need_rename:
        flag = detect_flag(name_decoded)
        new_name = f"{flag} WebFreedom"
    else:
        new_name = name_decoded

    return f"{base_part}#{urllib.parse.quote(new_name)}"


def decode_if_base64(text):
    """Проверяет строку и декодирует из Base64, если это необходимо."""
    text_stripped = text.strip()
    if text_stripped and not text_stripped.startswith(VALID_PROTOCOLS):
        try:
            missing_padding = len(text_stripped) % 4
            if missing_padding:
                text_stripped += '=' * (4 - missing_padding)
            decoded = base64.b64decode(text_stripped).decode("utf-8", errors="ignore")
            if decoded.strip().startswith(VALID_PROTOCOLS):
                return decoded
        except:
            pass
    return text


def main():
    sources = extract_urls_from_karing()
    if not sources:
        print("🛑 Нет доступных HTTP-ссылок. Скрипт остановлен.")
        return

    unique_configs = set()
    total_parsed_configs = 0

    print("\n📡 Скачивание и обработка источников...")

    with requests.Session() as session:
        for index, url in enumerate(sources, 1):
            try:
                response = session.get(url, timeout=12)
                if response.status_code != 200:
                    print(f"   ⚠️ [Источник {index}] Пропуск. Статус-код: {response.status_code}")
                    continue

                clean_text = decode_if_base64(response.text)
                for line in clean_text.splitlines():
                    line = line.strip()
                    if line.startswith(VALID_PROTOCOLS):
                        total_parsed_configs += 1
                        processed_line = process_and_rename(line)

                        if processed_line is not None:
                            unique_configs.add(processed_line)
                            
                print(f"   ✅ [Источник {index}] Успешно обработан")
            except Exception as e:
                print(f"   ⚠️ [Источник {index}] Ошибка сети: {e}")

    print("\n📊 ИТОГИ ОБРАБОТКИ:")
    print(f"   🔹 Всего найдено конфигураций: {total_parsed_configs}")
    print(f"   🔹 Сформировано уникальных серверов: {len(unique_configs)}")

    output_file = "webfreedom_test_output.txt"
    clean_configs = [cfg for cfg in unique_configs if cfg is not None]

    if clean_configs:
        # Укажи здесь то название подписки, которое должны увидеть пользователи
        subscription_name = "t.me/webfreedomvpn"
        
        # Формируем технический комментарий для приложения
        # Некоторые клиенты читают имя из первой строки, если она оформлена как специальный комментарий
        header_comment = f"//profile-title: {subscription_name}"
        
        # Собираем всё вместе: сначала имя подписки, потом сами сервера
        final_output = [header_comment] + sorted(clean_configs)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(final_output))
        print(f"💾 Файл '{output_file}' успешно сохранен с именем подписки '{subscription_name}'.")
    else:
        print("⚠️ Валидные конфигурации не найдены.")


if __name__ == "__main__":
    main()
