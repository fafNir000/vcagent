import json
import os
import time
from firecrawl import FirecrawlApp

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "banksconfig.json")
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "banks.json")

app = FirecrawlApp(api_key="fc-54f5f4a85c754601b17282e5a06e2043")

def run_scraper():
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Файл конфига не найден: {CONFIG_PATH}")
        return
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    final_data = {}
    for bank in config['banks']:
        bank_name = bank['name']
        print(f"\n🚀 Работаю с банком: {bank_name}")
        final_data[bank_name] = {"credits": "", "deposits": "", "branches": ""}
        mapping = {
            "credits": bank.get("credits_urls", []),
            "deposits": bank.get("deposits_urls", []),
            "branches": bank.get("branches_url", [])
        }
        for category, urls in mapping.items():
            combined_text = ""
            for url in urls:
                print(f"  📥 Скрейпинг {category}: {url}")
                try:
                    result = app.scrape(url,
                        only_main_content=True,
                        formats=["markdown"])
                    content = ""
                    if isinstance(result, dict):
                        content = result.get('markdown', "")
                    else:
                        content = getattr(result, 'markdown', "")
                    if content:
                        combined_text += content + "\n\n"
                        print(f"    ✅ Успешно! ({len(content)} симв.)")
                    else:
                        print(f"    ⚠️ Текст не найден. Ответ: {result}")
                    time.sleep(1) 
                except Exception as e:
                    print(f"    ❌ Ошибка: {e}")
            final_data[bank_name][category] = combined_text
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"\n✨ Готово! Файл наполнен: {DATA_PATH}")
if __name__ == "__main__":
    run_scraper()