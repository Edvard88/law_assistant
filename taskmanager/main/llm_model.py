from openai import OpenAI
import os
import time

OPENAI_API_KEY = ''

# Пути к вашим TXT файлам
file_paths = [
    "main/data/Иск_о_взыскании_долга.txt",
    "main/data/Иск_по_задолжности_по_алиментам.txt"
]

print("!!!!Я здесь", os.getcwd())

# 1. Читаем содержимое TXT файлов
def read_txt_files(file_paths):
    templates_content = ""
    for i, file_path in enumerate(file_paths):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            templates_content += f"\n\n{'='*50}\nШАБЛОН {i+1}: {os.path.basename(file_path)}\n{'='*50}\n{file_content}"
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
            templates_content += f"\n\nОшибка: не удалось прочитать файл {os.path.basename(file_path)}"
    print("Шаблон успешно сформирован")
    return templates_content


# Загружаем файлы в модель
def upload_files_in_the_model(file_paths):
  client = OpenAI(api_key=OPENAI_API_KEY)
  
  file_ids = []
#   for file_path in file_paths:
#       with open(file_path, "rb") as file_obj:
#           file = client.files.create(file=file_obj, purpose="user_data")  # Изменено на "batch"
#           file_ids.append(file.id)
#   print("Файлы загружены с ID:", file_ids)

  return file_ids

templates_content = read_txt_files(file_paths)
file_ids = upload_files_in_the_model(file_paths)


def model_predict(user_message):
  client = OpenAI(api_key=OPENAI_API_KEY)

  system_prompt = f"""

  Ты ассистент юриста. У тебя есть следующие шаблоны документов: {templates_content}


  ИНСТРУКЦИИ (ВЫПОЛНИ СТРОГО):
  1. Проанализируй ситуацию пользователя и определи тип спора
  2. Выбери ПОДХОДЯЩИЙ шаблон из приведенных выше
  3. ВЕРБАТИМНО воспроизведи структуру, форматирование и стиль выбранного шаблона
  4. Заполни пропуски ([...], ____ и т.д.) данными из запроса пользователя
  5. НИЧЕГО НЕ МЕНЯЙ в списке документов в приложении
  6. Сохрани все разделы, заголовки, нумерацию и оформление оригинала
  7. Если ситуация не подходит ни под один шаблон - вежливо сообщи об этом

  Важно: результат должен быть готов к печати и подаче в суд!

  """
  return "Тест"

#   ### Отправляем запрос
#   response = client.chat.completions.create(
#       model="gpt-4o",  # Можно использовать gpt-4o-mini для экономии
#       messages=[
#           {"role": "system",
#           "content": system_prompt},
#           {"role": "user",
#           "content": user_message,
#           "attachments": [
#                   {
#                       "file_id": file_ids[0],
#                       "tools": [{"type": "file_search"}]
#                   },
#                   {
#                       "file_id": file_ids[1],
#                       "tools": [{"type": "file_search"}]
#                   }
#               ]},

#       ],

#       temperature=0.1,    # Минимальная креативность - строгое следование шаблону
#       max_tokens=4000,    # Увеличиваем лимит для длинных документов
#       top_p=0.9           # Для более предсказуемых результатов
#   )

#   print("="*70)
#   print("✅ СОСТАВЛЕННЫЙ ИСК (готов к печати):")
#   print("="*70)
#   print(response.choices[0].message.content)

#   return response.choices[0].message.content

