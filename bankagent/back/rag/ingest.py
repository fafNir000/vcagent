import json
import os
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["PYTHONHTTPSVERIFY"] = "0"
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Настройка путей
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ПРАВИЛЬНЫЙ ПУТЬ: C:/D/bankagent/data/banks.json
DATA_PATH = os.path.join(BASE_DIR, 'data', 'banks.json')
# ПУТЬ К БАЗЕ: C:/D/bankagent/back/rag/chroma_db
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chroma_db')

def run_ingestion():
    print(f"📂 Чтение файла: {DATA_PATH}")
    
    if not os.path.exists(DATA_PATH):
        print(f"❌ Файл не найден по пути: {DATA_PATH}")
        return

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        banks_data = json.load(f)

    all_documents = []

    # Проходим по банкам (unibank, amiobank и т.д.)
    for bank_name, content_dict in banks_data.items():
        print(f"🏦 Обработка банка: {bank_name}")
        
        # Проходим по категориям (credits, deposits, branches)
        for category, text in content_dict.items():
            # Проверяем, что текст — это строка и она не пустая
            clean_text = str(text).strip()
            
            if len(clean_text) > 50:  # Игнорируем слишком короткие отрывки
                doc = Document(
                    page_content=clean_text,
                    metadata={"bank": bank_name, "category": category}
                )
                all_documents.append(doc)
                print(f"  ✅ Категория '{category}': добавлено {len(clean_text)} символов.")
            else:
                print(f"  ⚠️ Категория '{category}': слишком мало данных (пропуск).")

    if not all_documents:
        print("❌ Ошибка: Документы не собраны. Проверь структуру JSON еще раз.")
        return

    print(f"✂️ Всего документов собрано: {len(all_documents)}. Начинаю разбивку на чанки...")

    # Нарезка текста
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n# ", "\n## ", "\n\n", "\n", " "]
    )
    
    chunks = text_splitter.split_documents(all_documents)
    print(f"📦 Создано фрагментов (chunks): {len(chunks)}")

    # Эмбеддинги
    print("🧠 Загрузка модели эмбеддингов (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Сохранение в базу
    print(f"💾 Сохранение в ChromaDB: {DB_PATH}")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    print("✨ ГОТОВО! База данных создана и наполнена.")

if __name__ == "__main__":
    run_ingestion()