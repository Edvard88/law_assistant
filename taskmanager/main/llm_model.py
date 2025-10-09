from openai import OpenAI
import os
import time
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
 
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
Ты ассистент юриста.
Тебе нужно написать претензию и отправить ее получателю.
Проанализируй ситуацию пользователя и напиши текст претензии.

Перед анализом ситуации и выбором шаблона, извлеки из предоставленного текста все возможные данные об отправителе и получателе. 
Если какие-то данные отсутствуют в тексте, вместо них поставь длинную линию "________________________".

from_whom: [ФИО или название организации отправителя]
from_whom_address: [Почтовый адрес отправителя]
from_whom_tel: [Телефон отправителя]
from_whom_mail: [E-mail отправителя]
from_whom_inn: [ИНН отправителя]
from_whom_ogrn: [ОГРН/ОГРНИП отправителя]

to_whom: [ФИО или название организации получателя]
to_whom_address: [Почтовый адрес получателя]
to_whom_tel: [Телефон получателя]
to_whom_mail: [E-mail получателя]
to_whom_inn: [ИНН получателя]
to_whom_ogrn: [ОГРН получателя]
generated_issue_text: [Текст иска или претензии, который составь по входному тексту от пользователя]

Дополнительно:
1. Не надо в своем тексте писать "С уважением", "[Дата]", "[Подпись]" - это уже есть в шаблоне документа, куда будут вставляться данные.
2. Можешь основной текст generated_issue_text написать с переносом строк, выделяяя абзацы с html тегами, тк он будет вставляться в html шаблон.

Важно: результат должен быть готов к печати и подаче в суд!

  """
#   return "Тест"

  ### Отправляем запрос
  response = client.chat.completions.create(
      model="gpt-4o",  # Можно использовать gpt-4o-mini для экономии
      messages=[
          {"role": "system",
          "content": system_prompt},
          {"role": "user",
          "content": user_message,
         #  "attachments": [
         #          {
         #              "file_id": file_ids[0],
         #              "tools": [{"type": "file_search"}]
         #          },
         #          {
         #              "file_id": file_ids[1],
         #              "tools": [{"type": "file_search"}]
         #          }
         #      ]
              },

      ],

      temperature=0.1,    # Минимальная креативность - строгое следование шаблону
      max_tokens=4000,    # Увеличиваем лимит для длинных документов
      top_p=0.9           # Для более предсказуемых результатов
  )

#   print("="*70)
#   print("✅ СОСТАВЛЕННЫЙ ИСК (готов к печати):")
#   print("="*70)
#   print(response.choices[0].message.content)

  return response.choices[0].message.content

import re

def extract_after_label(text, label, end_marker=None):
    """
    Вспомогательная функция для извлечения значения после метки.
    """
    # Ищем до следующей метки или до generated_issue_text
    pattern = re.escape(label) + r'\s*:\s*(.*?)\s*(?=\n\w+|\n\n|generated_issue_text|\Z)'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        value = match.group(1).strip()
        if not value:
            return None
        return value
    return None

def model_to_whom(user_message):
    return extract_after_label(user_message, "to_whom")

def model_to_whom_address(user_message):
    return extract_after_label(user_message, "to_whom_address")

def model_to_whom_ogrn(user_message):
    return extract_after_label(user_message, "to_whom_ogrn")

def model_to_whom_inn(user_message):
    return extract_after_label(user_message, "to_whom_inn")

def model_to_whom_mail(user_message):
    return extract_after_label(user_message, "to_whom_mail")

def model_to_whom_tel(user_message):
    return extract_after_label(user_message, "to_whom_tel")

def model_from_whom(user_message):
    return extract_after_label(user_message, "from_whom")

def model_from_whom_address(user_message):
    return extract_after_label(user_message, "from_whom_address")

def model_from_whom_ogrn(user_message):
    return extract_after_label(user_message, "from_whom_ogrn")

def model_from_whom_inn(user_message):
    return extract_after_label(user_message, "from_whom_inn")

def model_from_whom_mail(user_message):
    return extract_after_label(user_message, "from_whom_mail")

def model_from_whom_tel(user_message):
    return extract_after_label(user_message, "from_whom_tel")

def model_issue_text(user_message):
    """
    Извлекает текст самой претензии (всё что после 'generated_issue_text:')
    """
    parts = user_message.split('generated_issue_text:')
    if len(parts) > 1:
        return parts[1].strip()
    return None