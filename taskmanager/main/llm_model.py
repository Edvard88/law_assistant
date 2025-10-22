from django.http import HttpResponse
from django.shortcuts import redirect
from openai import OpenAI
import os
import time
from dotenv import load_dotenv
import os

import pandas as pd

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect

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
    

    return response.choices[0].message.content


    return answer 

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


###########

import pandas as pd
import json

def business_model_predict(uploaded_files, template_content=None):
    """
    Генерирует претензии для бизнеса на основе загруженных файлов
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Сначала получаем точный список должников из отладочной функции
    expected_debtors = get_expected_debtors_list(uploaded_files)
    
    print("=== ОБЩАЯ ОТЛАДКА ===")
    debug_debt_calculation(uploaded_files)
    print("=== ОТЛАДКА ПЕРСОНАЛЬНЫХ ДАННЫХ ===")
    debug_personal_data_file(uploaded_files)

    # УСИЛЕННЫЙ ПРОМПТ С АВТОМАТИЧЕСКИМ СПИСКОМ ДОЛЖНИКОВ
    system_prompt = """
Ты ассистент юриста для массовой генерации претензий в СНТ.

ТВОЯ ЗАДАЧА: найти ВСЕХ должников с долгом > 60000 рублей без исключений.

КРИТИЧЕСКИ ВАЖНО:
1. ПРОАНАЛИЗИРУЙ КАЖДУЮ строку файла начислений
2. НЕ ПРОПУСТИ НИ ОДНОГО должника с долгом > 60000 рублей
3. ВКЛЮЧИ ВСЕХ из предоставленного списка ожидаемых должников

ШАГИ АНАЛИЗА:
1. Проанализируй ВСЕ строки из файла начислений
2. Сгруппируй по уникальной комбинации "ФИО + Адрес участка в СНТ"
3. Для каждой группы суммируй ВСЕ значения долга
4. Включи ВСЕХ, где суммарный долг > 60000 рублей

ПРАВИЛА ГРУППИРОВКИ:
- Разные участки у одного ФИО = РАЗНЫЕ должники
- Одинаковые ФИО+участок с несколькими строками = СУММИРУЙ долги
- NaN значения в долге считай как 0

Структура JSON для каждого должника:
{
    "fio": "ФИО должника (точно как в файле)",
    "address": "Адрес проживания", 
    "snt_address": "Адрес СНТ (дом и участок)",
    "kadastr_number": "Кадастровый номер",
    "email": "Электронная почта",
    "phone": "Телефон", 
    "debt_amount": 12345.67,
    "contract_number": "Номер договора"
}

Верни ТОЛЬКО JSON массив!
"""

    try:
        # Читаем и подготавливаем данные
        accruals_content = ""
        personal_content = ""
        
        for filename, filepath in uploaded_files.items():
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                try:
                    df = pd.read_excel(filepath)
                    print(f"Файл {filename}: {len(df)} строк, колонки: {df.columns.tolist()}")
                    
                    if 'персональные' in filename.lower():
                        personal_content = format_personal_data_for_llm(df, filename)
                    else:
                        accruals_content = format_accruals_data_for_llm(df, filename)
                        
                except Exception as e:
                    print(f"Ошибка чтения Excel файла {filename}: {e}")
                    return []
        
        # Формируем запрос с АВТОМАТИЧЕСКИМ списком должников
        user_content = f"""
ПРОАНАЛИЗИРУЙ ЭТИ ДАННЫЕ И НАЙДИ ВСЕХ ДОЛЖНИКОВ С ДОЛГОМ > 60000 РУБЛЕЙ:

ФАЙЛ НАЧИСЛЕНИЙ (долги):
{accruals_content}

ФАЙЛ ПЕРСОНАЛЬНЫХ ДАННЫХ (контакты):
{personal_content}

ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ:
По нашим точным расчетам должно быть {expected_debtors['count']} должников с долгом > 60000 рублей.
Если ты находишь меньше - ТЫ ПРОПУСТИЛ ДОЛЖНИКОВ!

ОСОБОЕ ВНИМАНИЕ НА ЭТИХ ДОЛЖНИКОВ (они точно есть в файле и должны быть включены):
{expected_debtors['list']}

ПЕРЕПРОВЕРЬ ВСЕ СТРОКИ и убедись, что включил ВСЕХ {expected_debtors['count']} должников!

Верни JSON массив со ВСЕМИ найденными должниками.
"""

        print("Отправляем запрос к GPT-4o для анализа данных...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1,
            max_tokens=10000
        )

        result_text = response.choices[0].message.content
        print(f"Получен ответ от GPT-4o: {result_text}")
        
        return parse_business_response(result_text)
        
    except Exception as e:
        print(f"Ошибка в business_model_predict: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_expected_debtors_list(uploaded_files):
    """Получает точный список должников из файла начислений с гибким поиском колонок"""
    try:
        import pandas as pd
        from collections import defaultdict
        
        # Находим файл начислений
        accruals_file = None
        for filename, filepath in uploaded_files.items():
            if any(keyword in filename.lower() for keyword in ['начисления', 'оплаты', 'accruals', 'payments']):
                accruals_file = filepath
                break
        
        if not accruals_file:
            return {'count': 0, 'list': 'Файл начислений не найден'}
        
        df = pd.read_excel(accruals_file)
        
        # ГИБКИЙ ПОИСК КОЛОНОК
        fio_column = find_column_by_keywords(df, ['контрагент', 'фио', 'name', 'фам'])
        address_column = find_column_by_keywords(df, ['дом', 'участок', 'адрес', 'address', 'снт'])
        debt_column = find_column_by_keywords(df, ['долг', 'задолженность', 'debt', 'сумма', 'начислено'])
        
        print(f"Найдены колонки: ФИО='{fio_column}', Адрес='{address_column}', Долг='{debt_column}'")
        
        if not fio_column or not debt_column:
            print("Не найдены обязательные колонки (ФИО или Долг)")
            return {'count': 0, 'list': 'Не найдены обязательные колонки'}
        
        # Группируем по ФИО и адресу
        debt_groups = defaultdict(float)
        
        for index, row in df.iterrows():
            fio = row.get(fio_column, '')
            address = row.get(address_column, '') if address_column else ''
            debt_str = row.get(debt_column, '')
            
            if not fio or pd.isna(fio):
                continue
                
            debt = 0.0
            if pd.notna(debt_str) and debt_str != '':
                try:
                    debt = float(debt_str)
                except (ValueError, TypeError):
                    debt = 0.0
            
            # Создаем ключ группировки
            if address and pd.notna(address):
                key = f"{fio} | {address}"
            else:
                key = f"{fio}"
                
            debt_groups[key] += debt
        
        # Формируем список должников с долгом > 60k
        debtors_list = []
        for key, total_debt in sorted(debt_groups.items(), key=lambda x: x[1], reverse=True):
            if total_debt > 60000:
                debtors_list.append(f"- {key}: {total_debt:.2f} руб.")
        
        # Форматируем для промпта
        list_text = "\n".join(debtors_list)
        
        return {
            'count': len(debtors_list),
            'list': list_text
        }
        
    except Exception as e:
        print(f"Ошибка получения списка должников: {e}")
        return {'count': 0, 'list': f'Ошибка: {e}'}

def find_column_by_keywords(df, keywords):
    """Находит колонку по ключевым словам в названии"""
    for col in df.columns:
        col_lower = str(col).lower()
        for keyword in keywords:
            if keyword in col_lower:
                return col
    return None

def format_accruals_data_for_llm(df, filename):
    """Форматирует данные начислений для LLM с гибким определением колонок"""
    content = f"ФАЙЛ: {filename}\n"
    content += f"КОЛОНКИ: {df.columns.tolist()}\n"
    content += f"ВСЕГО СТРОК: {len(df)}\n\n"
    
    # Находим колонки гибко
    fio_column = find_column_by_keywords(df, ['контрагент', 'фио', 'name', 'фам'])
    address_column = find_column_by_keywords(df, ['дом', 'участок', 'адрес', 'address', 'снт'])
    debt_column = find_column_by_keywords(df, ['долг', 'задолженность', 'debt', 'сумма', 'начислено'])
    
    content += f"ОПРЕДЕЛЕННЫЕ КОЛОНКИ:\n"
    content += f"- ФИО: {fio_column}\n"
    content += f"- Адрес участка: {address_column}\n" 
    content += f"- Долг: {debt_column}\n\n"
    
    # Показываем примеры данных
    content += "ПЕРВЫЕ 20 СТРОК ДЛЯ АНАЛИЗА:\n"
    for i in range(min(20, len(df))):
        row = df.iloc[i]
        fio = row.get(fio_column, '') if fio_column else 'НЕТ КОЛОНКИ ФИО'
        address = row.get(address_column, '') if address_column else 'НЕТ КОЛОНКИ АДРЕСА'
        debt = row.get(debt_column, '') if debt_column else 'НЕТ КОЛОНКИ ДОЛГА'
        content += f"Строка {i}: ФИО='{fio}' | Участок='{address}' | Долг='{debt}'\n"
    
    content += f"\nПОЛНЫЕ ДАННЫЕ ({len(df)} строк):\n"
    content += df.to_string() + "\n\n"
    
    return content

def format_personal_data_for_llm(df, filename):
    """Форматирует персональные данные для LLM с гибким поиском колонок"""
    content = f"ФАЙЛ: {filename}\n"
    content += f"КОЛОНКИ: {df.columns.tolist()}\n"
    content += f"ВСЕГО СТРОК: {len(df)}\n\n"
    
    # Гибкий поиск колонок
    fio_column = find_column_by_keywords(df, ['контрагент', 'фио', 'name', 'фам'])
    address_column = find_column_by_keywords(df, ['адрес', 'address', 'проживан'])
    snt_address_column = find_column_by_keywords(df, ['снт', 'участок', 'дом'])
    kadastr_column = find_column_by_keywords(df, ['кадастр', 'kadastr', 'номер'])
    email_column = find_column_by_keywords(df, ['email', 'почта', 'mail'])
    phone_column = find_column_by_keywords(df, ['телефон', 'phone', 'тел'])
    contract_column = find_column_by_keywords(df, ['договор', 'contract', 'номер'])
    
    content += f"ОПРЕДЕЛЕННЫЕ КОЛОНКИ:\n"
    content += f"- ФИО: {fio_column}\n"
    content += f"- Адрес проживания: {address_column}\n"
    content += f"- Адрес СНТ: {snt_address_column}\n"
    content += f"- Кадастровый номер: {kadastr_column}\n"
    content += f"- Email: {email_column}\n"
    content += f"- Телефон: {phone_column}\n"
    content += f"- Договор: {contract_column}\n\n"
    
    if fio_column:
        content += "ДАННЫЕ ИЗ ФАЙЛА:\n"
        for i in range(len(df)):
            row = df.iloc[i]
            fio_value = row.get(fio_column)
            
            if pd.notna(fio_value) and str(fio_value).strip() != '':
                content += f"Строка {i}:\n"
                content += f"  ФИО: {fio_value}\n"
                
                # Показываем другие колонки
                for col, col_name in [
                    (address_column, "Адрес проживания"),
                    (snt_address_column, "Адрес СНТ"), 
                    (kadastr_column, "Кадастровый номер"),
                    (email_column, "Email"),
                    (phone_column, "Телефон"),
                    (contract_column, "Договор")
                ]:
                    if col:
                        value = row.get(col)
                        if pd.notna(value) and str(value).strip() != '':
                            content += f"  {col_name}: {value}\n"
                content += "\n"
    
    return content

def parse_business_response(response_text):
    """Парсит ответ от модели в структурированные данные"""
    try:
        import json
        import re
        
        # Ищем JSON в ответе
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
            
            # ВАЛИДАЦИЯ И ОБРАБОТКА ДАННЫХ
            processed_data = []
            for item in data:
                # Проверяем обязательные поля
                if not item.get('fio') or not item.get('snt_address'):
                    print(f"Пропущена запись без ФИО или адреса СНТ: {item}")
                    continue
                
                # Обрабатываем debt_amount
                debt_amount = item.get('debt_amount', 0)
                try:
                    debt_amount = float(debt_amount)
                except (ValueError, TypeError):
                    debt_amount = 0.0
                
                # Пропускаем если долг меньше порога
                if debt_amount < 60000:
                    continue
                
                # Проверяем наличие персональных данных
                has_personal_data = (
                    item.get('address') != '_________________________' and 
                    item.get('address') != '' and
                    item.get('address') is not None and
                    len(str(item.get('address', '')).strip()) > 5
                )
                
                processed_item = {
                    "fio": str(item['fio']).strip(),
                    "address": item.get('address', '_________________________'),
                    "snt_address": item.get('snt_address', '_________________________'),
                    "kadastr_number": item.get('kadastr_number', '_________________________'),
                    "email": item.get('email', '_________________________'),
                    "phone": item.get('phone', '_________________________'),
                    "debt_amount": debt_amount,
                    "contract_number": item.get('contract_number', '_________________________'),
                    "has_personal_data": has_personal_data
                }
                
                processed_data.append(processed_item)
            
            print(f"GPT-4o обработал: {len(processed_data)} записей с долгом > 60,000 руб.")
            
            # ВЫВОД СТАТИСТИКИ
            unique_fios = len(set(item['fio'] for item in processed_data))
            with_personal_data = sum(1 for item in processed_data if item['has_personal_data'])
            
            print(f"Статистика: {unique_fios} уникальных ФИО, {with_personal_data} с персональными данными")
            
            return processed_data
        else:
            print("JSON не найден в ответе GPT-4o")
            return []
            
    except Exception as e:
        print(f"Ошибка парсинга ответа GPT-4o: {e}")
        return []
            
    except Exception as e:
        print(f"Ошибка парсинга ответа LLM: {e}")
        return []
    

def format_accruals_data_for_llm(df, filename):
    """Форматирует данные начислений для лучшего понимания LLM"""
    content = f"ФАЙЛ: {filename}\n"
    content += f"КОЛОНКИ: {df.columns.tolist()}\n"
    content += f"ВСЕГО СТРОК: {len(df)}\n\n"
    
    # Показываем примеры данных
    content += "ПЕРВЫЕ 10 СТРОК ДЛЯ АНАЛИЗА:\n"
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        fio = row.get('контрагенты', '')
        address = row.get('Дом_участок_в_СНТ', '')
        debt = row.get('долг на 13.10.2025 на 07:00', '')
        content += f"Строка {i}: ФИО='{fio}' | Участок='{address}' | Долг='{debt}'\n"
    
    content += f"\nПОЛНЫЕ ДАННЫЕ ({len(df)} строк):\n"
    content += df.to_string() + "\n\n"
    
    return content

def format_personal_data_for_llm(df, filename):
    """Форматирует персональные данные для лучшего понимания LLM"""
    content = f"ФАЙЛ: {filename}\n"
    content += f"КОЛОНКИ: {df.columns.tolist()}\n"
    content += f"ВСЕГО СТРОК: {len(df)}\n\n"
    
    # Ищем данные в разных форматах
    data_found = False
    
    # Пробуем найти колонку с ФИО
    fio_column = None
    for col in df.columns:
        col_str = str(col).lower()
        if any(keyword in col_str for keyword in ['контрагент', 'фио', 'name', 'фам']):
            fio_column = col
            break
    
    if fio_column:
        content += f"КОЛОНКА С ФИО: '{fio_column}'\n\n"
        
        # Показываем непустые строки
        content += "ДАННЫЕ ИЗ ФАЙЛА:\n"
        for i in range(len(df)):
            row = df.iloc[i]
            fio_value = row.get(fio_column)
            
            if pd.notna(fio_value) and str(fio_value).strip() != '':
                data_found = True
                content += f"Строка {i}:\n"
                content += f"  ФИО: {fio_value}\n"
                
                # Показываем другие колонки
                for col in df.columns:
                    if col != fio_column:
                        value = row.get(col)
                        if pd.notna(value) and str(value).strip() != '':
                            content += f"  {col}: {value}\n"
                content += "\n"
    
    if not data_found:
        content += "Файл не содержит четко структурированных данных. Будут использованы заполнители.\n"
        content += "ПОЛНЫЕ ДАННЫЕ:\n" + df.to_string() + "\n"
    
    return content


def debug_debt_calculation(uploaded_files):
    """Отладочная функция для проверки суммирования долгов"""
    import pandas as pd
    from collections import defaultdict
    
    # Находим файл начислений
    accruals_file = None
    for filename, filepath in uploaded_files.items():
        if any(keyword in filename.lower() for keyword in ['начисления', 'оплаты', 'accruals', 'payments']):
            accruals_file = filepath
            break
    
    if not accruals_file:
        print("DEBUG: Файл начислений не найден")
        return
    
    try:
        df = pd.read_excel(accruals_file)
        print(f"DEBUG: Загружен файл начислений, {len(df)} строк")
        print(f"DEBUG: Колонки: {df.columns.tolist()}")
        
        # Группируем по ФИО и участку
        debt_groups = defaultdict(float)
        
        for index, row in df.iterrows():
            fio = row.get('контрагенты', '')
            address = row.get('Дом_участок_в_СНТ', '')
            debt_str = row.get('долг на 13.10.2025 на 07:00', '')
            
            # Пропускаем пустые ФИО
            if not fio or pd.isna(fio):
                continue
                
            # Обрабатываем долг
            debt = 0.0
            if pd.notna(debt_str) and debt_str != '':
                try:
                    debt = float(debt_str)
                except (ValueError, TypeError):
                    debt = 0.0
            
            key = f"{fio} | {address}"
            debt_groups[key] += debt
        
        # Выводим всех с долгом > 60k
        print("\nDEBUG: ДОЛЖНИКИ С ДОЛГОМ > 60,000 руб.:")
        found_count = 0
        for key, total_debt in sorted(debt_groups.items(), key=lambda x: x[1], reverse=True):
            if total_debt > 60000:
                found_count += 1
                print(f"  {found_count:2d}. {key}: {total_debt:.2f} руб.")
        
        print(f"DEBUG: Всего найдено {found_count} должников с долгом > 60,000 руб.")
            
    except Exception as e:
        print(f"DEBUG: Ошибка при отладке: {e}")



def debug_specific_debtors(uploaded_files):
    """Отладочная функция для конкретных пропущенных должников"""
    import pandas as pd
    
    accruals_file = None
    for filename, filepath in uploaded_files.items():
        if any(keyword in filename.lower() for keyword in ['начисления', 'оплаты']):
            accruals_file = filepath
            break
    
    if not accruals_file:
        return
    
    try:
        df = pd.read_excel(accruals_file)
        
        # Ищем конкретных должников
        target_names = [
            "Петренко Татьяна Ивановна",
            "Пангин Андрей Александрович", 
            "Нестеренко Марта Сергеевна",
            "Лазгиян Ханум Изоевна"
        ]
        
        print("\n=== ОТЛАДКА КОНКРЕТНЫХ ДОЛЖНИКОВ ===")
        for name in target_names:
            matches = df[df['контрагенты'].str.contains(name, na=False)]
            if not matches.empty:
                print(f"\n{name}:")
                for idx, row in matches.iterrows():
                    debt = row.get('долг на 13.10.2025 на 07:00', '')
                    address = row.get('Дом_участок_в_СНТ', '')
                    print(f"  - {address}: {debt}")
            else:
                print(f"\n{name}: НЕ НАЙДЕН в файле!")
                
    except Exception as e:
        print(f"DEBUG ERROR: {e}")


def debug_personal_data_file(uploaded_files):
    """Отладочная функция для анализа файла персональных данных"""
    import pandas as pd
    
    personal_file = None
    for filename, filepath in uploaded_files.items():
        if any(keyword in filename.lower() for keyword in ['персональные', 'personal', 'данные']):
            personal_file = filepath
            break
    
    if not personal_file:
        print("DEBUG: Файл персональных данных не найден")
        return
    
    try:
        df = pd.read_excel(personal_file)
        print(f"DEBUG: Загружен файл персональных данных, {len(df)} строк")
        print(f"DEBUG: Колонки: {df.columns.tolist()}")
        print(f"DEBUG: Первые 5 строк:")
        print(df.head().to_string())
        
        # Ищем конкретные ФИО в персональных данных
        target_names = [
            "Пангин Андрей Александрович",
            "Нестеренко Марта Сергеевна", 
            "Лазгиян Ханум Изоевна",
            "Пупкова Татьяна Алексеевна",  # для сравнения
            "Петренко Татьяна Ивановна"    # для сравнения
        ]
        
        print("\n=== ПОИСК КОНКРЕТНЫХ ФИО В ПЕРСОНАЛЬНЫХ ДАННЫХ ===")
        
        # Определяем колонку с ФИО
        fio_column = None
        for col in df.columns:
            if 'контрагент' in str(col).lower() or 'фио' in str(col).lower():
                fio_column = col
                break
        
        if not fio_column:
            print("❌ Колонка с ФИО не найдена")
            return
        
        print(f"Колонка с ФИО: {fio_column}")
        
        for name in target_names:
            # Ищем точное совпадение
            exact_matches = df[df[fio_column] == name]
            # Ищем частичное совпадение
            partial_matches = df[df[fio_column].str.contains(name, na=False)]
            
            print(f"\n{name}:")
            print(f"  Точные совпадения: {len(exact_matches)}")
            print(f"  Частичные совпадения: {len(partial_matches)}")
            
            if not exact_matches.empty:
                print(f"  ✅ Найден в персональных данных")
                row = exact_matches.iloc[0]
                print(f"  Адрес: {row.get('Адрес проживания', 'НЕТ')}")
                print(f"  Адрес СНТ: {row.get('Адрес СНТ', 'НЕТ')}")
            else:
                print(f"  ❌ НЕ найден в персональных данных")
                
    except Exception as e:
        print(f"DEBUG: Ошибка при анализе персональных данных: {e}")




def process_files_locally(uploaded_files):
    """Локальная обработка файлов без OpenAI"""
    try:
        # ... существующий код ...
        
        # Формируем итоговые данные
        claims_data = []
        
        for key, total_debt in debt_groups.items():
            if total_debt > 60000:  # Только долги > 60,000
                details = debt_details[key]
                fio = details['fio']
                address = details['address']
                
                # Ищем персональные данные
                personal_info = personal_data.get(fio, {})
                
                # Определяем, есть ли полные персональные данные
                has_address = personal_info.get('address', '_________________________') != '_________________________'
                has_snt_address = address if address else personal_info.get('snt_address', '_________________________') != '_________________________'
                has_email = personal_info.get('email', '_________________________') != '_________________________'
                has_phone = personal_info.get('phone', '_________________________') != '_________________________'
                
                # Считаем, что данные полные если есть адрес и адрес СНТ
                has_full_data = has_address and has_snt_address
                
                claim = {
                    "fio": fio,
                    "address": personal_info.get('address', '_________________________'),
                    "snt_address": address if address else personal_info.get('snt_address', '_________________________'),
                    "kadastr_number": personal_info.get('kadastr_number', '_________________________'),
                    "email": personal_info.get('email', '_________________________'),
                    "phone": personal_info.get('phone', '_________________________'),
                    "debt_amount": total_debt,
                    "contract_number": '_________________________',
                    "has_personal_data": has_full_data  # Только если есть адрес и адрес СНТ
                }
                
                claims_data.append(claim)
        
        print(f"✅ Локальная обработка завершена: {len(claims_data)} должников с долгом > 60,000 руб.")
        
        # Выводим статистику
        with_full_data = sum(1 for claim in claims_data if claim['has_personal_data'])
        print(f"📊 Статистика: {len(claims_data)} должников, {with_full_data} с полными персональными данными")
        
        return claims_data
        
    except Exception as e:
        print(f"❌ Ошибка локальной обработки: {e}")
        import traceback
        traceback.print_exc()
        return []
    

# def process_business_files_fallback(uploaded_files):
#     """Fallback метод для обработки файлов если LLM не работает"""
#     claims_data = []
    
#     try:
#         import pandas as pd
        
#         # Ищем файлы по названиям
#         personal_data_file = None
#         accruals_file = None
        
#         for filename, filepath in uploaded_files.items():
#             if 'персональные_данные' in filename.lower() or 'персональные данные' in filename.lower():
#                 personal_data_file = filepath
#             elif 'начисления' in filename.lower() or 'оплаты' in filename.lower():
#                 accruals_file = filepath
        
#         print(f"Fallback: personal_file={personal_data_file}, accruals_file={accruals_file}")
        
#         if personal_data_file and accruals_file:
#             # Читаем Excel файлы
#             try:
#                 personal_df = pd.read_excel(personal_data_file, header=7)  # Пропускаем заголовки
#             except:
#                 personal_df = pd.read_excel(personal_data_file)  # Если не получается, читаем без пропуска
            
#             accruals_df = pd.read_excel(accruals_file)
            
#             print(f"Fallback: personal_df колонки: {personal_df.columns.tolist()}")
#             print(f"Fallback: accruals_df колонки: {accruals_df.columns.tolist()}")
            
#             # Обрабатываем персональные данные
#             processed_count = 0
#             for index, row in personal_df.iterrows():
#                 # Получаем ФИО из колонки 'Контрагенты' или похожей
#                 fio = None
#                 for col in personal_df.columns:
#                     if 'контрагент' in str(col).lower() or 'фио' in str(col).lower():
#                         fio = row.get(col)
#                         break
                
#                 if not fio or pd.isna(fio) or fio == '':
#                     continue
                
#                 print(f"Fallback: Обрабатываем {fio}")
                
#                 # Получаем остальные данные
#                 address = '_________________________'
#                 snt_address = '_________________________'
#                 kadastr = '_________________________'
#                 email = '_________________________'
#                 phone = '_________________________'
#                 contract_number = '_________________________'
                
#                 # Ищем адрес
#                 for col in personal_df.columns:
#                     col_lower = str(col).lower()
#                     if 'адрес' in col_lower and 'снт' not in col_lower:
#                         addr_val = row.get(col)
#                         if pd.notna(addr_val) and str(addr_val).strip() != '':
#                             address = str(addr_val)
#                             break
                
#                 # Ищем адрес СНТ
#                 for col in personal_df.columns:
#                     col_lower = str(col).lower()
#                     if 'адрес' in col_lower and 'снт' in col_lower:
#                         snt_val = row.get(col)
#                         if pd.notna(snt_val) and str(snt_val).strip() != '':
#                             snt_address = str(snt_val)
#                             break
                
#                 # Ищем кадастровый номер
#                 for col in personal_df.columns:
#                     col_lower = str(col).lower()
#                     if 'кадастр' in col_lower:
#                         kad_val = row.get(col)
#                         if pd.notna(kad_val) and str(kad_val).strip() != '':
#                             kadastr = str(kad_val)
#                             break
                
#                 # Ищем email
#                 for col in personal_df.columns:
#                     col_lower = str(col).lower()
#                     if 'email' in col_lower or 'почта' in col_lower or 'mail' in col_lower:
#                         email_val = row.get(col)
#                         if pd.notna(email_val) and str(email_val).strip() != '':
#                             email = str(email_val)
#                             break
                
#                 # Ищем телефон
#                 for col in personal_df.columns:
#                     col_lower = str(col).lower()
#                     if 'телефон' in col_lower or 'phone' in col_lower or 'tel' in col_lower:
#                         phone_val = row.get(col)
#                         if pd.notna(phone_val) and str(phone_val).strip() != '':
#                             phone = str(phone_val)
#                             break
                
#                 # Ищем номер договора
#                 for col in personal_df.columns:
#                     col_lower = str(col).lower()
#                     if 'договор' in col_lower or 'contract' in col_lower or 'номер' in col_lower:
#                         contract_val = row.get(col)
#                         if pd.notna(contract_val) and str(contract_val).strip() != '':
#                             contract_number = str(contract_val)
#                             break
                
#                 # Проверяем, есть ли персональные данные
#                 has_personal_data = (address != '_________________________')
                
#                 # Находим долг
#                 debt = find_debt_in_accruals(accruals_df, str(fio))
                
#                 claim_data = {
#                     "fio": str(fio).strip(),
#                     "address": address,
#                     "snt_address": snt_address,
#                     "kadastr_number": kadastr,
#                     "email": email,
#                     "phone": phone,
#                     "contract_number": contract_number,
#                     "debt_amount": float(debt) if debt else 0.0,
#                     "has_personal_data": has_personal_data
#                 }
                
#                 print(f"Fallback: Данные для {fio}: долг = {debt}, has_personal_data = {has_personal_data}, адрес = {address}, договор = {contract_number}")
                
#                 # Добавляем только если есть долг
#                 if debt and debt > 0:
#                     claims_data.append(claim_data)
#                     processed_count += 1
            
#             print(f"Fallback: Обработано {processed_count} записей с долгом")
        
#         print(f"Fallback: Всего найдено {len(claims_data)} записей с долгом")
#         return claims_data
        
#     except Exception as e:
#         print(f"Ошибка в fallback обработке: {e}")
#         import traceback
#         traceback.print_exc()
#         return []
        

# def find_debt_in_accruals(accruals_df, fio):
#     """Находит долг по ФИО в файле начислений"""
#     try:
#         # Ищем строки, содержащие ФИО (частичное совпадение)
#         for col in accruals_df.columns:
#             if 'контрагент' in col.lower() or 'фио' in col.lower() or 'name' in col.lower():
#                 matching_rows = accruals_df[accruals_df[col].astype(str).str.contains(fio, na=False)]
#                 if not matching_rows.empty:
#                     # Ищем колонку с долгом
#                     for debt_col in accruals_df.columns:
#                         if 'долг' in debt_col.lower():
#                             debt_value = matching_rows[debt_col].iloc[0]
#                             if pd.notna(debt_value) and debt_value != '':
#                                 try:
#                                     return float(debt_value)
#                                 except:
#                                     return 0.0
#         return 0.0
#     except Exception as e:
#         print(f"Ошибка поиска долга для {fio}: {e}")
#         return 0.0
    

# def process_business_files(request):
#     """Обработка загруженных файлов и генерация претензий через LLM"""
#     if request.method == 'POST' and request.FILES:
#         uploaded_files = request.FILES.getlist('files')
        
#         print(f"Получено файлов: {len(uploaded_files)}")
#         for file in uploaded_files:
#             print(f"Файл: {file.name}, размер: {file.size}")
        
#         # Временное хранение файлов
#         temp_files = {}
#         fs = FileSystemStorage(location=tempfile.gettempdir())
        
#         try:
#             # Сохраняем файлы временно
#             for file in uploaded_files:
#                 filename = fs.save(f"business_temp_{file.name}", file)
#                 temp_files[file.name] = fs.path(filename)
            
#             # Читаем шаблон если есть
#             template_content = None
#             for filename, filepath in temp_files.items():
#                 if 'претензия_снг' in filename.lower() or 'шаблон' in filename.lower():
#                     with open(filepath, 'r', encoding='utf-8') as f:
#                         template_content = f.read()
#                     break
            
#             print("Вызываем LLM модель...")
#             # Обрабатываем файлы через LLM модель
#             claims_data = business_model_predict(temp_files, template_content)
            
#             print(f"LLM вернула {len(claims_data)} записей")
            
#             # Фильтруем должников с долгом > 60,000 рублей
#             filtered_claims = [
#                 claim for claim in claims_data 
#                 if claim.get('debt_amount', 0) > 60000
#             ]
            
#             print(f"После фильтрации >60k: {len(filtered_claims)} записей")
            
#             # Генерируем PDF файлы
#             generated_pdfs = []
#             for claim in filtered_claims:
#                 pdf_content = generate_single_business_pdf(claim, template_content)
#                 if pdf_content:
#                     filename = f"претензия_{claim['fio'].replace(' ', '_')}.pdf"
#                     generated_pdfs.append({
#                         'filename': filename,
#                         'content': pdf_content,
#                         'claim': claim
#                     })
            
#             print(f"Сгенерировано PDF: {len(generated_pdfs)}")
            
#             # Создаем ZIP архив
#             zip_buffer = create_business_zip_archive(generated_pdfs)
            
#             # Сохраняем в сессии
#             request.session['business_zip'] = zip_buffer.getvalue().decode('latin-1')
#             request.session['generated_count'] = len(generated_pdfs)
#             request.session['total_claims'] = len(claims_data)
#             request.session['filtered_claims'] = len(filtered_claims)
            
#             context = {
#                 'generated_count': len(generated_pdfs),
#                 'total_claims': len(claims_data),
#                 'filtered_claims': len(filtered_claims),
#                 'claims_data': filtered_claims,
#                 'has_zip': len(generated_pdfs) > 0
#             }
            
#             return render(request, 'main/process_business_files.html', context)
            
#         except Exception as e:
#             print(f"Ошибка обработки файлов: {str(e)}")
#             import traceback
#             traceback.print_exc()
            
#             # Очистка временных файлов в случае ошибки
#             for filepath in temp_files.values():
#                 if os.path.exists(filepath):
#                     os.remove(filepath)
            
#             return HttpResponse(f'Ошибка обработки файлов: {str(e)}')
        
#         finally:
#             # Всегда очищаем временные файлы
#             for filepath in temp_files.values():
#                 if os.path.exists(filepath):
#                     try:
#                         os.remove(filepath)
#                     except:
#                         pass
    
#     return redirect('business')


# def process_business_data_fallback(personal_file, accruals_file):
#     """Альтернативная обработка без использования LLM"""
#     import pandas as pd
#     import re
    
#     # Загружаем данные
#     personal_df = pd.read_excel(personal_file)
#     accruals_df = pd.read_excel(accruals_file)
    
#     # Переименуем колонки для удобства
#     personal_df.columns = ['index1', 'index2', 'Контрагенты', 'Адрес проживания', 'Адрес СНТ', 'Кадастровый номер', 'Электронная почта', 'Телефон']
    
#     # Автоматически находим колонку с долгом (ищем в нескольких вариантах)
#     debt_column = None
#     possible_debt_columns = []
    
#     for col in accruals_df.columns:
#         col_lower = str(col).lower()
#         if any(keyword in col_lower for keyword in ['долг', 'задолженность', 'debt', 'arrears']):
#             possible_debt_columns.append(col)
    
#     # Выбираем наиболее подходящую колонку
#     if possible_debt_columns:
#         # Предпочитаем колонки с "долг" в названии
#         for col in possible_debt_columns:
#             if 'долг' in str(col).lower():
#                 debt_column = col
#                 break
#         if debt_column is None:
#             debt_column = possible_debt_columns[0]  # берем первую подходящую
#         print(f"Fallback: Найдена колонка с долгом: {debt_column}")
#     else:
#         # Если не нашли колонку с долгом, пробуем найти числовую колонку в конце
#         numeric_columns = []
#         for col in accruals_df.columns:
#             if accruals_df[col].dtype in ['float64', 'int64']:
#                 numeric_columns.append(col)
        
#         if numeric_columns:
#             debt_column = numeric_columns[-1]  # последняя числовая колонка
#             print(f"Fallback: Используем числовую колонку как долг: {debt_column}")
#         else:
#             debt_column = accruals_df.columns[-1]  # последняя колонка вообще
#             print(f"Fallback: Колонка с долгом не найдена, используем последнюю колонку: {debt_column}")
    
#     results = []
    
#     # Обрабатываем только строки с Протоколом №1 (актуальные данные)
#     protocol_rows = accruals_df[accruals_df['номер договора'].str.contains('Протокол № 1', na=False)]
    
#     print(f"Fallback: Найдено {len(protocol_rows)} записей с Протоколом №1")
    
#     for _, row in protocol_rows.iterrows():
#         name = row['контрагенты']
#         debt = row[debt_column] if debt_column in row else 0
        
#         # Пропускаем если долга нет или он 0 или пустая строка
#         if pd.isna(debt) or debt == 0 or debt == '':
#             continue
            
#         print(f"Fallback: Обрабатываем {name}")
#         print(f"Fallback: Долг из колонки '{debt_column}': {debt}")
        
#         # Ищем в персональных данных
#         name_clean = name.split('(')[0].strip()
#         personal_data = personal_df[personal_df['Контрагенты'].str.contains(name_clean, na=False)]
        
#         has_personal_data = len(personal_data) > 0
#         address = ""
#         contract_number = ""
        
#         if has_personal_data:
#             personal_row = personal_data.iloc[0]
#             address = personal_row['Адрес проживания']
#             contract_number = personal_row['Кадастровый номер']
#             print(f"Fallback: Найдены персональные данные: адрес={address}, договор={contract_number}")
#         else:
#             print(f"Fallback: Персональные данные не найдены")
        
#         # Извлекаем адрес СНТ из названия контрагента
#         snt_address_match = re.search(r'\(([^)]+)\)', name)
#         snt_address = snt_address_match.group(1) if snt_address_match else ""
        
#         results.append({
#             'fio': name,
#             'address': address,
#             'snt_address': snt_address,
#             'kadastr_number': contract_number,
#             'email': '_________________________',
#             'phone': '_________________________', 
#             'contract_number': contract_number,
#             'debt_amount': debt,
#             'has_personal_data': has_personal_data
#         })
    
#     print(f"Fallback: Всего найдено {len(results)} записей с долгом")
#     return results