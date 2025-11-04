from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.conf import settings
from xhtml2pdf import pisa
import io
import os
from datetime import datetime

# Create your views here.
from .models import LawIssue
from .forms import LawIssueForm
from .llm_model import model_predict, model_issue_text,\
                        model_to_whom, model_to_whom_address, model_to_whom_ogrn, model_to_whom_inn, model_to_whom_mail, model_to_whom_tel, \
                        model_from_whom, model_from_whom_address, model_from_whom_ogrn, model_from_whom_inn, model_from_whom_mail, model_from_whom_tel

from django.http import HttpResponse
from django.template.loader import render_to_string
#from weasyprint import HTML

from django.template.loader import get_template
from xhtml2pdf import pisa

import pandas as pd
import zipfile
import tempfile
import os
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect

import pandas as pd
import os
from datetime import datetime


import logging
# Настройка логгера
logger = logging.getLogger(__name__)


# def index(request):
#     return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')

def get_signature():
    pass

def ensure_directory_exists(directory_path):
    """Создает директорию, если она не существует"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def save_pdf_to_file(pdf_content, file_path):
    """Сохраняет PDF контент в файл"""
    try:
        with open(file_path, 'wb') as f:
            f.write(pdf_content.getvalue())
        return True
    except Exception as e:
        print(f"Ошибка сохранения PDF: {str(e)}")
        return False


def generate_issue_text_v2(claim_text):
    """Генерирует текст претензии с использованием модели и шаблона"""
    generated_issue = model_predict(claim_text)
    print("!!!!!claim_text", claim_text)
    print("!!!!!generated_issue", generated_issue)
    print("!!!model_issue_text(generated_issue)", model_issue_text(generated_issue))
    
    # Создаем контекст для шаблона
    context = {
        'to_whom': model_to_whom(generated_issue),
        'to_whom_address': model_to_whom_address(generated_issue),
        'to_whom_ogrn': model_to_whom_ogrn(generated_issue),
        'to_whom_inn': model_to_whom_inn(generated_issue),
        'to_whom_mail': model_to_whom_mail(generated_issue),
        'to_whom_tel': model_to_whom_tel(generated_issue),
        'from_whom': model_from_whom(generated_issue),
        'from_whom_address': model_from_whom_address(generated_issue),
        'from_whom_ogrn': model_from_whom_ogrn(generated_issue),
        'from_whom_inn': model_from_whom_inn(generated_issue),
        'from_whom_mail': model_from_whom_mail(generated_issue),
        'from_whom_tel': model_from_whom_tel(generated_issue),
        'generated_issue_text': model_issue_text(generated_issue),
    }
    
    # Генерируем полный HTML текст претензии
    full_claim_html = render_to_string('main/pdf_template.html', context)
    return full_claim_html




import base64
from django.core.files.base import ContentFile
import re

def index(request):
    # Обработка GET запроса - показываем пустую форму
    if request.method != 'POST':
        form = LawIssueForm()
        context = {
            'form': form,
            'show_generated_issue': False,
            'show_signature': False,
            'current_step': 1
        }
        return render(request, "main/index.html", context)
    
    # Обработка POST запроса
    form = LawIssueForm(request.POST)
    
    if not form.is_valid():
        context = {
            'form': form,
            'show_generated_issue': False,
            'show_signature': False,
            'current_step': 1,
            'error': 'Форма была неверной'
        }
        return render(request, "main/index.html", context)
    
    data = form.cleaned_data
    title = data.get('title')
    generated_issue = data.get('generated_issue')
    signature = data.get('signature')
    
    # Определяем логику отображения
    current_step = 1
    show_generated_issue = False
    show_signature = False
    signature_image = None
    from_whom = "_________________________"
    cleaned_generated_issue = None  # Добавляем переменную для очищенного текста
    
    if title:
        # Всегда получаем имя отправителя, если есть title
        from_whom = model_from_whom(title) or "_________________________"
        
        if not generated_issue:
            # Шаг 2: Генерируем текст претензии
            generated_issue_text = generate_issue_text_v2(title)
            instance = form.save(commit=False)
            instance.generated_issue = generated_issue_text
            instance.save()
            form = LawIssueForm(instance=instance)
            show_generated_issue = True
            show_signature = False
            current_step = 2
            
        elif generated_issue and not signature:
            # Шаг 3: Текст есть, но нет подписи - показываем поле подписи
            instance = form.save()
            show_generated_issue = True
            show_signature = True
            current_step = 3
            
        elif generated_issue and signature:
            # Шаг 4: Все данные есть - показываем модальное окно предпросмотра
            instance = form.save()
            show_generated_issue = True
            show_signature = True
            current_step = 4
            
            # Конвертируем подпись в base64 для отображения в HTML
            if signature:
                # Убедимся, что подпись в правильном формате
                if signature.startswith('data:image/png;base64,'):
                    signature_image = signature
                else:
                    signature_image = f"data:image/png;base64,{signature}"
            
            # Очищаем сгенерированный текст от дублирующего блока подписи
            cleaned_generated_issue = generated_issue
            # Удаляем стандартные блоки подписи с помощью регулярных выражений
            cleaned_generated_issue = re.sub(r'<p[^>]*>.*[Пп]одпись\s*:.*</p>', '', cleaned_generated_issue)
            cleaned_generated_issue = re.sub(r'[Пп]одпись\s*:.*\n', '', cleaned_generated_issue)
            cleaned_generated_issue = re.sub(r'<p[^>]*>.*[Дд]ата\s*:.*</p>', '', cleaned_generated_issue)
            cleaned_generated_issue = re.sub(r'[Дд]ата\s*:.*\n', '', cleaned_generated_issue)
            #cleaned_generated_issue = re.sub(r'_{10,}', '', cleaned_generated_issue)
            
            # Если после очистки текст стал пустым, используем оригинальный
            if not cleaned_generated_issue.strip():
                cleaned_generated_issue = generated_issue
    
    else:
        # Шаг 1: Нет title
        current_step = 1
        show_generated_issue = False
        show_signature = False
    
    context = {
        'form': form,
        'show_generated_issue': show_generated_issue,
        'show_signature': show_signature,
        'current_step': current_step,
        'signature_image': signature_image,
        'from_whom': from_whom,
        'cleaned_generated_issue': cleaned_generated_issue,  # Передаем очищенный текст
    }
    
    return render(request, "main/index.html", context)


def generate_pdf_from_html(html_content):
    """Генерирует PDF из HTML контента с правильной кодировкой"""
    pdf_file = io.BytesIO()
    
    # Настройки для правильного отображения кириллицы
    pisa_status = pisa.CreatePDF(
        html_content, 
        dest=pdf_file,
        encoding='utf-8',
        link_callback=None
    )
    
    if pisa_status.err:
        print(f"Ошибка генерации PDF: {pisa_status.err}")
        return None
    
    pdf_file.seek(0)
    return pdf_file


def generate_pdf_weasyprint(html_content):
    """Генерация PDF через WeasyPrint (работает лучше на Mac)"""
    try:
        from weasyprint import HTML
        from weasyprint.text.fonts import FontConfiguration
        
        font_config = FontConfiguration()
        
        pdf_file = io.BytesIO()
        
        HTML(
            string=html_content,
            encoding='utf-8'
        ).write_pdf(
            pdf_file,
            font_config=font_config
        )
        
        pdf_file.seek(0)
        print("✓ PDF generated successfully with WeasyPrint")
        return pdf_file
        
    except Exception as e:
        print(f"❌ WeasyPrint error: {e}")
        # Fallback на xhtml2pdf
        print("Trying xhtml2pdf fallback...")
        return generate_pdf_from_html(html_content)

def generate_claim_pdf_context(claim_text, generated_issue_text, signature_data=None):
    """Генерирует контекст для PDF претензии с подписью"""
    context = {
        'to_whom': model_to_whom(claim_text) or "_________________________",
        'to_whom_address': model_to_whom_address(claim_text) or "_________________________",
        'to_whom_ogrn': model_to_whom_ogrn(claim_text) or "_________________________",
        'to_whom_inn': model_to_whom_inn(claim_text) or "_________________________",
        'to_whom_mail': model_to_whom_mail(claim_text) or "_________________________",
        'to_whom_tel': model_to_whom_tel(claim_text) or "_________________________",
        'from_whom': model_from_whom(claim_text) or "_________________________",
        'from_whom_address': model_from_whom_address(claim_text) or "_________________________",
        'from_whom_ogrn': model_from_whom_ogrn(claim_text) or "_________________________",
        'from_whom_inn': model_from_whom_inn(claim_text) or "_________________________",
        'from_whom_mail': model_from_whom_mail(claim_text) or "_________________________",
        'from_whom_tel': model_from_whom_tel(claim_text) or "_________________________",
        'generated_issue_text': generated_issue_text,
        'signature_data': signature_data,  # Добавляем данные подписи
    }
    return context

def generate_agreement_pdf_context(claim_text, signature_data=None):
    """Генерирует контекст для PDF пользовательского соглашения"""
    return {
        'from_whom': model_from_whom(claim_text),
        'from_whom_ogrn': model_from_whom_ogrn(claim_text),
        'from_whom_inn': model_from_whom_inn(claim_text),
        'from_whom_address': model_from_whom_address(claim_text),
        'signature_data': signature_data,  # Добавляем подпись
    }

def send_pdf_email(request):
    """Отправляет PDF файлы на email и сохраняет их в папки проекта"""
    logger.info("=== send_pdf_email called ===")
    
    if request.method == 'POST':
        user_email = request.POST.get('user_email')
        user_agreement = request.POST.get('user_agreement')
        title = request.POST.get('title')
        generated_issue = request.POST.get('generated_issue')
        signature = request.POST.get('signature')
        
        logger.info(f"Received data - Email: {user_email}, Agreement: {user_agreement}")
        logger.info(f"Title length: {len(title) if title else 0}")
        logger.info(f"Generated issue length: {len(generated_issue) if generated_issue else 0}")
        logger.info(f"Signature present: {bool(signature)}")
        
        if not user_agreement:
            logger.warning("User agreement not accepted")
            return HttpResponse('Необходимо согласие с пользовательским соглашением')
        
        if not user_email:
            logger.warning("No email provided")
            return HttpResponse('Необходимо указать email адрес')
        
        try:
            # Если есть подпись, заменяем прочерки на изображение подписи
            if signature:
                # Создаем HTML для подписи с вашим стилем
                signature_html = f'<img src="{signature}" style="height: 45px; max-width: 150px; display: block; filter: hue-rotate(220deg) saturate(4) brightness(0.7) contrast(3) drop-shadow(0 0 0 blue) drop-shadow(0 0 0 blue);" alt="Подпись">'
                
                # Заменяем прочерки на подпись
                final_html = generated_issue.replace(
                    '<!-- Если подписи нет, отображаем черту для подписи --> _________________________',
                    signature_html
                )
            else:
                # Оставляем как есть (прочерки)
                final_html = generated_issue
            
            # Генерируем PDF претензии с подписью из финального HTML
            claim_pdf = generate_pdf_weasyprint(final_html)
            
            if not claim_pdf:
                return HttpResponse('Ошибка генерации PDF')
            
            # Генерируем PDF пользовательского соглашения
            logger.info("Generating agreement PDF...")
            agreement_context = generate_claim_pdf_context(title, generated_issue, signature)
            agreement_html = render_to_string('main/user_agreement.html', agreement_context)
            agreement_pdf = generate_pdf_weasyprint(agreement_html)
            
            if not claim_pdf:
                logger.error("Claim PDF generation failed")
                return HttpResponse('Ошибка генерации PDF претензии')
            
            if not agreement_pdf:
                logger.error("Agreement PDF generation failed")
                return HttpResponse('Ошибка генерации PDF соглашения')
            
            logger.info("PDF files generated successfully")
            
            # Сохраняем PDF файлы в папки проекта
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Пути для сохранения
            claim_directory = "data/generated_issue_pdf"
            agreement_directory = "data/generated_user_agreement"
            
            # Создаем директории, если они не существуют
            ensure_directory_exists(claim_directory)
            ensure_directory_exists(agreement_directory)
            
            # Имена файлов
            claim_filename = f"претензия_{timestamp}.pdf"
            agreement_filename = f"пользовательское_соглашение_{timestamp}.pdf"
            
            claim_filepath = os.path.join(claim_directory, claim_filename)
            agreement_filepath = os.path.join(agreement_directory, agreement_filename)
            
            # Сохраняем файлы
            logger.info(f"Saving PDF files: {claim_filepath}, {agreement_filepath}")
            claim_saved = save_pdf_to_file(claim_pdf, claim_filepath)
            agreement_saved = save_pdf_to_file(agreement_pdf, agreement_filepath)
            
            if not claim_saved or not agreement_saved:
                logger.error("Failed to save PDF files to disk")
                return HttpResponse('Ошибка сохранения PDF файлов')
            
            logger.info("PDF files saved successfully")
            
            # Сбрасываем позицию в файлах для отправки по email
            claim_pdf.seek(0)
            agreement_pdf.seek(0)
            
            # ===== РАБОЧАЯ РУЧНАЯ SMTP ОТПРАВКА =====
            logger.info("=== STARTING SMTP SEND ===")
            
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.application import MIMEApplication
            
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['Subject'] = 'Ваша претензия - AI Law Assistant'
            msg['From'] = settings.DEFAULT_FROM_EMAIL
            msg['To'] = user_email
            
            # ЗАМЕНА: Указываем email адреса для копий
            copy_emails = ['edvard88@inbox.ru', '89036414195@mail.ru']
            msg['Cc'] = ', '.join(copy_emails)
            
            # Текст письма
            body = f"""Уважаемый пользователь,

Во вложении вы найдете:
1. Сгенерированную претензию
2. Пользовательское соглашение

Файлы также сохранены в нашей системе.

С уважением,
AI Law Assistant"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Прикрепляем PDF файлы
            claim_attachment = MIMEApplication(claim_pdf.read(), _subtype='pdf')
            claim_attachment.add_header('Content-Disposition', 'attachment', filename='претензия.pdf')
            msg.attach(claim_attachment)
            
            agreement_attachment = MIMEApplication(agreement_pdf.read(), _subtype='pdf')
            agreement_attachment.add_header('Content-Disposition', 'attachment', filename='пользовательское_соглашение.pdf')
            msg.attach(agreement_attachment)
            
            # Формируем список получателей (основной + копии)
            recipients = [user_email] + copy_emails
            
            logger.info(f"Recipients: {recipients}")
            
            # Подключаемся к SMTP
            logger.info(f"Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            
            if getattr(settings, 'EMAIL_USE_SSL', False):
                logger.info("Using SMTP_SSL")
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                logger.info("Using SMTP with TLS")
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                if getattr(settings, 'EMAIL_USE_TLS', False):
                    server.starttls()
            
            # Логинимся
            logger.info("Logging in...")
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            logger.info("Login successful")
            
            # Отправляем
            logger.info("Sending email...")
            server.sendmail(settings.DEFAULT_FROM_EMAIL, recipients, msg.as_string())
            logger.info("Email sent via SMTP")
            
            # Закрываем соединение
            server.quit()
            logger.info("SMTP connection closed")
            # ===== КОНЕЦ РУЧНОЙ SMTP ОТПРАВКИ =====
            
            # Сохраняем в модель LawIssue
            logger.info("Saving to LawIssue model...")
            law_issue = LawIssue.objects.create(
                title=title,
                generated_issue=generated_issue,
                signature=signature
            )
            
            # Сохраняем файлы в модель
            with open(claim_filepath, 'rb') as claim_file:
                law_issue.generated_claim_pdf.save(claim_filename, claim_file)
            
            with open(agreement_filepath, 'rb') as agreement_file:
                law_issue.user_agreement.save(agreement_filename, agreement_file)
            
            logger.info("Data saved to database successfully")
            
            # success_message = f"""
            # PDF успешно отправлен на вашу почту {user_email}!
            
            # Проверьте:
            # 1. Папку "Входящие"
            # 2. Папку "Спам" 
            # 3. Папку "Отправленные" в {settings.EMAIL_HOST_USER}
            
            # Копии отправлены на: {', '.join(copy_emails)}
            
            # Файлы также сохранены на сервере:
            # - Претензия: {claim_filepath}
            # - Пользовательское соглашение: {agreement_filepath}
            # """
            
            # logger.info("=== send_pdf_email completed successfully ===")
            # return HttpResponse(success_message)
            
            context = {
                'user_email': user_email,
            }
            
            logger.info("=== send_pdf_email completed successfully ===")
            return render(request, 'main/success_mail_page.html', context)
            
        except smtplib.SMTPAuthenticationError as auth_error:
            logger.error(f"SMTP AUTHENTICATION ERROR: {auth_error}")
            return HttpResponse(f'Ошибка аутентификации: {auth_error}')
        except smtplib.SMTPException as smtp_error:
            logger.error(f"SMTP ERROR: {smtp_error}")
            return HttpResponse(f'Ошибка SMTP: {smtp_error}')
        except Exception as e:
            logger.error(f"General error in send_pdf_email: {str(e)}", exc_info=True)
            return HttpResponse(f'Ошибка: {str(e)}')
    
    logger.warning("send_pdf_email called with non-POST method")
    return redirect('home')


from weasyprint import HTML
import tempfile


def generate_pdf_xhtml2pdf(request):
    """Генерирует PDF для скачивания и сохраняет в папку"""
    if request.method == 'POST':
        title = request.POST.get('title')
        generated_issue = request.POST.get('generated_issue')
        
        context = generate_claim_pdf_context(title, generated_issue)
        html = render_to_string('main/pdf_template.html', context)
        
        # Генерируем PDF через WeasyPrint
        pdf_file = generate_pdf_weasyprint(html)  # ← ИЗМЕНИЛИ НА WeasyPrint
        
        if not pdf_file:
            return HttpResponse('Ошибка генерации PDF')
        
        # Сохраняем PDF в папку
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        claim_directory = "data/generated_issue_pdf"
        ensure_directory_exists(claim_directory)
        
        claim_filename = f"претензия_{timestamp}.pdf"
        claim_filepath = os.path.join(claim_directory, claim_filename)
        
        if save_pdf_to_file(pdf_file, claim_filepath):
            print(f"PDF сохранен: {claim_filepath}")
        
        # Сбрасываем позицию для отдачи пользователю
        pdf_file.seek(0)
        
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{claim_filename}"'
        
        return response
    
    return redirect('home')


def download_pdf_only(request):
    """Только сохраняет PDF в папку без отправки на email"""
    if request.method == 'POST':
        title = request.POST.get('title')
        generated_issue = request.POST.get('generated_issue')
        signature = request.POST.get('signature')
        
        # Если есть подпись, заменяем прочерки на изображение подписи
        if signature:
            # Создаем HTML для подписи с вашим стилем
            signature_html = f'<img src="{signature}" style="height: 45px; max-width: 150px; display: block; filter: hue-rotate(220deg) saturate(4) brightness(0.7) contrast(3) drop-shadow(0 0 0 blue) drop-shadow(0 0 0 blue);" alt="Подпись">'
            
            # Заменяем прочерки на подпись
            final_html = generated_issue.replace(
                '<!-- Если подписи нет, отображаем черту для подписи --> _________________________',
                signature_html
            )
        else:
            # Оставляем как есть (прочерки)
            final_html = generated_issue
        
        # Генерируем PDF из финального HTML
        claim_pdf = generate_pdf_weasyprint(final_html)
        
        if not claim_pdf:
            return HttpResponse('Ошибка генерации PDF')
        
        # Сохраняем PDF файлы в папки проекта
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        claim_directory = "data/generated_issue_pdf"
        agreement_directory = "data/generated_user_agreement"
        
        ensure_directory_exists(claim_directory)
        ensure_directory_exists(agreement_directory)
        
        claim_filename = f"претензия_{timestamp}.pdf"
        agreement_filename = f"пользовательское_соглашение_{timestamp}.pdf"
        
        claim_filepath = os.path.join(claim_directory, claim_filename)
        agreement_filepath = os.path.join(agreement_directory, agreement_filename)
        
        # Сохраняем файлы
        claim_saved = save_pdf_to_file(claim_pdf, claim_filepath)
        
        # Для соглашения используем обычный подход
        agreement_context = generate_agreement_pdf_context(title, signature)
        agreement_html = render_to_string('main/user_agreement.html', agreement_context)
        agreement_pdf = generate_pdf_weasyprint(agreement_html)
        agreement_saved = save_pdf_to_file(agreement_pdf, agreement_filepath)
        
        if claim_saved and agreement_saved:
            # Сбрасываем позицию для отдачи пользователю
            claim_pdf.seek(0)
            
            response = HttpResponse(claim_pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{claim_filename}"'
            
            # Сохраняем в модель
            law_issue = LawIssue.objects.create(
                title=title,
                generated_issue=generated_issue,
                signature=signature
            )
            
            with open(claim_filepath, 'rb') as claim_file:
                law_issue.generated_claim_pdf.save(claim_filename, claim_file)
            
            with open(agreement_filepath, 'rb') as agreement_file:
                law_issue.user_agreement.save(agreement_filename, agreement_file)
            
            return response
        else:
            return HttpResponse('Ошибка сохранения PDF файлов')
    
    return redirect('home')


#############
from .llm_model import business_model_predict #, process_business_files_fallback
import json
from django.core.files.base import ContentFile



def ensure_business_directory():
    """Создает директорию для бизнес-данных если не существует"""
    business_dir = os.path.join("data", "business")
    ensure_directory_exists(business_dir)
    return business_dir

def get_existing_debtors_csv_path():
    """Возвращает путь к CSV файлу с историей должников"""
    business_dir = ensure_business_directory()
    return os.path.join(business_dir, "debtors_history.csv")


def append_debtors_to_csv(claims_data):
    """Добавляет должников в CSV файл только с полными данными"""
    try:
        csv_path = get_existing_debtors_csv_path()
        
        # Инициализируем CSV если не существует или пустой
        init_debtors_csv()
        
        # Подготавливаем данные для CSV
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        csv_data = []
        for claim in claims_data:
            # ВАЖНО: claims_data уже должна содержать только тех, у кого has_personal_data = True
            # но на всякий случай проверяем еще раз
            if not claim.get('has_personal_data', False):
                continue
                
            fio = claim.get('fio', '')
            snt_address = claim.get('snt_address', '')
            debt = claim.get('debt_amount', 0)
            
            # Дополнительная проверка на заполнители
            if (fio == '_________________________' or 
                snt_address == '_________________________' or
                not fio or not snt_address or
                debt <= 60000):
                continue
                
            # Используем правильные названия колонок
            csv_data.append({
                'дата': current_date,
                'контрагенты': fio,
                'дом_участок_в_СНТ': snt_address,
                'долг': debt
            })
        
        if not csv_data:
            print("ℹ️ Нет данных для добавления в CSV")
            return False
        
        # Создаем DataFrame
        df_new = pd.DataFrame(csv_data)
        
        # Читаем существующие данные
        df_existing = pd.read_csv(csv_path)
        
        # Объединяем, убирая дубликаты по контрагентам и участку
        df_combined = pd.concat([df_existing, df_new]).drop_duplicates(
            subset=['контрагенты', 'дом_участок_в_СНТ'], 
            keep='last'
        )
        
        # Сохраняем обратно
        df_combined.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ В CSV добавлено {len(df_new)} должников с полными данными")
        print(f"📁 Всего записей в CSV: {len(df_combined)}")
        
        # Выводим отладочную информацию о добавленных записях
        for _, row in df_new.iterrows():
            print(f"   📝 Добавлен: {row['контрагенты']} | {row['дом_участок_в_СНТ']} | {row['долг']} руб.")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при записи в CSV: {e}")
        import traceback
        traceback.print_exc()
        return False

def init_debtors_csv():
    """Инициализирует CSV файл если он не существует"""
    csv_path = get_existing_debtors_csv_path()
    if not os.path.exists(csv_path):
        # Создаем пустой CSV с правильными заголовками
        df = pd.DataFrame(columns=['дата', 'контрагенты', 'дом_участок_в_СНТ', 'долг'])
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ Создан новый CSV файл: {csv_path}")

def get_previously_contacted_debtors():
    """Возвращает список должников, которым уже отправлялись претензии"""
    try:
        csv_path = get_existing_debtors_csv_path()
        
        if not os.path.exists(csv_path):
            return []
        
        df = pd.read_csv(csv_path)
        
        # Возвращаем список с новыми названиями колонок
        contacted_debtors = []
        for _, row in df.iterrows():
            contacted_debtors.append({
                'contractor': row.get('контрагенты', ''),
                'snt_address': row.get('дом_участок_в_СНТ', ''),
                'date_added': row.get('дата', ''),
                'debt_amount': row.get('долг', 0)
            })
        
        print(f"📋 Прочитано из CSV: {len(contacted_debtors)} записей")
        return contacted_debtors
        
    except Exception as e:
        print(f"❌ Ошибка чтения CSV: {e}")
        return []
        
    except Exception as e:
        print(f"Ошибка чтения CSV: {e}")
        return []

def is_debtor_previously_contacted(fio, snt_address):
    """Проверяет, отправлялась ли претензия этому должнику ранее"""
    contacted_debtors = get_previously_contacted_debtors()
    
    for debtor in contacted_debtors:
        if (debtor['contractor'] == fio and 
            debtor['snt_address'] == snt_address):
            print(f"✅ Найден в истории: {fio} | {snt_address}")
            return True
    
    print(f"❌ Не найден в истории: {fio} | {snt_address}")
    return False


def business_dashboard(request):
    """Главная страница для бизнеса"""
    return render(request, 'main/business_dashboard.html')

def process_business_files(request):
    """Обработка загруженных файлов и генерация претензий"""
    if request.method == 'POST' and request.FILES:
        uploaded_files = request.FILES.getlist('files')
        
        # Временное хранение файлов
        temp_files = {}
        fs = FileSystemStorage(location=tempfile.gettempdir())
        
        try:
            # Сохраняем файлы временно
            for file in uploaded_files:
                filename = fs.save(f"business_temp_{file.name}", file)
                temp_files[file.name] = fs.path(filename)
            
            # Обрабатываем файлы через LLM - теперь получаем ВСЕХ должников
            claims_data = business_model_predict(temp_files, None)
            
            # ВАЖНО: claims_data теперь содержит ВСЕХ должников с долгом > 0
            all_debtors = claims_data
            
            # Считаем статистику
            total_debtors = len(all_debtors)
            debtors_over_60k = sum(1 for claim in all_debtors if claim.get('debt_amount', 0) > 60000)
            
            print(f"🔍 Отладочная информация:")
            print(f"   Всего claims_data: {total_debtors}")
            print(f"   С долгом > 60k: {debtors_over_60k}")
            
            # Получаем список ранее оповещенных должников
            previously_contacted = get_previously_contacted_debtors()
            
            # ФИЛЬТРУЕМ для генерации PDF только по долгу > 60,000
            all_debtors_over_60k = []
            already_contacted_claims = []
            
            for claim in claims_data:
                debt = claim.get('debt_amount', 0)
                
                # Для генерации PDF берем только с долгом > 60k
                if debt > 60000:
                    fio = claim.get('fio', '')
                    snt_address = claim.get('snt_address', '')
                    
                    if is_debtor_previously_contacted(fio, snt_address):
                        contacted_date = None
                        for contacted in previously_contacted:
                            if (contacted['contractor'] == fio and 
                                contacted['snt_address'] == snt_address):
                                contacted_date = contacted['date_added']
                                break
                        
                        claim_with_date = claim.copy()
                        claim_with_date['date_contacted'] = contacted_date
                        already_contacted_claims.append(claim_with_date)
                    else:
                        all_debtors_over_60k.append(claim)
            
            print(f"   Уже в истории: {len(already_contacted_claims)}")
            
            # Генерируем PDF файлы только для новых должников с долгом > 60k и полными данными
            generated_pdfs = []
            for claim in all_debtors_over_60k:
                if claim.get('has_personal_data', False):
                    pdf_result = generate_single_business_pdf(claim, None)
                    if pdf_result:
                        generated_pdfs.append(pdf_result)
            
            # Создаем ZIP архив
            zip_buffer = create_business_zip_archive(generated_pdfs)
            
            # Сохраняем в сессии
            request.session['business_zip'] = zip_buffer.getvalue().decode('latin-1')
            request.session['generated_count'] = len(generated_pdfs)
            request.session['total_claims'] = total_debtors  # ВСЕ должники
            request.session['debtors_over_60k'] = debtors_over_60k  # Количество с долгом > 60k
            request.session['filtered_claims'] = len(all_debtors_over_60k)  # Для генерации PDF
            request.session['all_debtors'] = all_debtors  # ВСЕ должники для отображения
            request.session['all_claims_data'] = all_debtors  # Для рассылки - ВСЕ должники
            request.session['already_contacted_claims'] = already_contacted_claims
            
            context = {
                'generated_count': len(generated_pdfs),
                'total_claims': total_debtors,  # ВСЕ должники
                'debtors_over_60k': debtors_over_60k,  # Количество с долгом > 60k
                'filtered_claims': len(all_debtors_over_60k),  # Для генерации PDF
                'all_debtors': all_debtors,  # ВСЕ должники для отображения
                'already_contacted_claims': already_contacted_claims,
                'has_zip': len(generated_pdfs) > 0
            }
            
            return render(request, 'main/process_business_files.html', context)
            
        except Exception as e:
            # Очистка временных файлов в случае ошибки
            for filepath in temp_files.values():
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            return HttpResponse(f'Ошибка обработки файлов: {str(e)}')
        
        finally:
            # Всегда очищаем временные файлы
            for filepath in temp_files.values():
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
    
    return redirect('business')

def generate_business_claims(request):
    """Генерация претензий для бизнеса"""
    if request.method == 'POST':
        claims_data = request.session.get('business_claims_data', [])
        template_content = request.session.get('business_template')
        
        if not claims_data:
            return HttpResponse('Нет данных для генерации')
        
        # Фильтруем только тех, у кого есть долг и нет существующей претензии
        valid_claims = []
        for claim in claims_data:
            if claim.get('debt_amount', 0) > 0:
                # Проверяем БД на существующую претензию
                if not BusinessClaim.objects.filter(fio=claim['fio'], is_generated=True).exists():
                    valid_claims.append(claim)
        
        # Генерируем PDF файлы
        generated_files = []
        for claim in valid_claims:
            pdf_content = generate_single_business_pdf(claim, template_content)
            if pdf_content:
                # Сохраняем в БД
                business_claim = BusinessClaim(
                    fio=claim['fio'],
                    address=claim['address'],
                    snt_address=claim['snt_address'],
                    kadastr_number=claim['kadastr_number'],
                    email=claim['email'],
                    phone=claim['phone'],
                    debt_amount=claim['debt_amount'],
                    is_generated=True
                )
                
                filename = f"претензия_{claim['fio'].replace(' ', '_')}.pdf"
                business_claim.generated_pdf.save(filename, ContentFile(pdf_content))
                business_claim.save()
                
                generated_files.append({
                    'filename': filename,
                    'content': pdf_content,
                    'claim': claim
                })
        
        # Создаем ZIP архив
        zip_buffer = create_business_zip_archive(generated_files)
        
        # Сохраняем ZIP в сессии
        request.session['business_zip'] = zip_buffer.getvalue().decode('latin-1')
        request.session['generated_count'] = len(generated_files)
        
        context = {
            'generated_count': len(generated_files),
            'skipped_count': len(claims_data) - len(generated_files),
            'claims_data': valid_claims
        }
        
        return render(request, 'main/generate_business_claims.html', context)
    
    return redirect('process_business_files')

def generate_single_business_pdf(claim_data, template_content=None):
    """Генерация одного PDF файла по шаблону СНТ с участком в названии и содержании"""
    try:
        # Если шаблон не передан, используем стандартный из файла
        if not template_content:
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'main', 'issue_snt.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        
        # Получаем данные участка для использования в PDF
        snt_address = claim_data.get('snt_address', '')
        fio = claim_data.get('fio', '')
        
        # Создаем понятное название файла с участком
        address_clean = snt_address.replace(' ', '_').replace(',', '').replace('.', '')
        filename_safe = f"{fio.replace(' ', '_')}_{address_clean}" if snt_address else f"{fio.replace(' ', '_')}"
        
        # Подготавливаем контекст с участком
        context = {
            'ФИО': fio,
            'Адрес проживания': claim_data.get('address', '_________________________'),
            'Адрес СНТ': snt_address,  # Обязательно включаем участок
            'кадастровый номер': claim_data.get('kadastr_number', '_________________________'),
            'Эл. почта': claim_data.get('email', '_________________________'),
            'Телефон': claim_data.get('phone', '_________________________'),
            'долг': f"{claim_data.get('debt_amount', 0):,.2f}",
            'Номер договора': claim_data.get('contract_number', '_________________________'),
            # Добавляем отдельные поля для гибкости в шаблоне
            'fio': fio,
            'address': claim_data.get('address', '_________________________'),
            'snt_address': snt_address,
            'debt_amount': f"{claim_data.get('debt_amount', 0):,.2f}",
            'debt_amount_raw': claim_data.get('debt_amount', 0)
        }
        
        # Заменяем плейсхолдеры в шаблоне
        html_content = template_content
        for key, value in context.items():
            placeholder = f'{{{key}}}'
            html_content = html_content.replace(placeholder, str(value))
        
        # Дополнительная замена для старых шаблонов
        html_content = html_content.replace('{участок}', snt_address)
        html_content = html_content.replace('{Участок}', snt_address)
        html_content = html_content.replace('{адрес_снт}', snt_address)
        html_content = html_content.replace('{Адрес СНТ}', snt_address)
        
        # Генерируем PDF
        pdf_file = generate_pdf_weasyprint(html_content)
        
        if pdf_file:
            return {
                'filename': f"претензия_{filename_safe}.pdf",
                'content': pdf_file.getvalue(),
                'claim': claim_data
            }
        
        return None
        
    except Exception as e:
        print(f"Ошибка генерации PDF для {claim_data.get('fio', 'unknown')}: {e}")
        import traceback
        traceback.print_exc()
        return None
        

def create_business_zip_archive(generated_files):
    """Создание ZIP архива с PDF файлами с правильными названиями"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_data in generated_files:
            zip_file.writestr(file_data['filename'], file_data['content'])
    
    zip_buffer.seek(0)
    return zip_buffer

def download_business_zip(request):
    """Скачивание ZIP архива с претензиями и сохранение в CSV только при скачивании"""
    zip_content = request.session.get('business_zip', '')
    all_claims_data = request.session.get('all_claims_data', [])  # Это уже отфильтрованные данные!
    
    if not zip_content:
        return HttpResponse('Файл не найден')
    
    # Сохраняем в CSV ТОЛЬКО при нажатии на скачивание
    if all_claims_data:
        print(f"💾 Сохраняем в CSV при скачивании: {len(all_claims_data)} записей")
        success = append_debtors_to_csv(all_claims_data)
        if success:
            print("✅ Данные успешно сохранены в CSV")
        else:
            print("❌ Ошибка сохранения в CSV")
    
    # Декодируем обратно из latin-1
    zip_bytes = zip_content.encode('latin-1')
    
    response = HttpResponse(zip_bytes, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="business_claims.zip"'
    
    # Очищаем сессию после скачивания
    if 'business_zip' in request.session:
        del request.session['business_zip']
    if 'all_claims_data' in request.session:
        del request.session['all_claims_data']
    
    return response

def send_business_emails(request):
    """Отправка писем с претензиями"""
    if request.method == 'POST':
        zip_content = request.session.get('business_zip', '')
        generated_count = request.session.get('generated_count', 0)
        
        if not zip_content:
            return HttpResponse('Нет данных для отправки')
        
        try:
            # Декодируем ZIP
            zip_bytes = zip_content.encode('latin-1')
            
            # Создаем письмо
            subject = f'Сгенерированные претензии для СНТ ({generated_count} шт.)'
            body = f"""
            Во вложении архив с {generated_count} сгенерированными претензиями.
            
            Сгенерировано: {datetime.now().strftime("%Y-%m-%d %H:%M")}
            """
            
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['edvard88@inbox.ru'],
            )
            
            # Прикрепляем ZIP архив
            email.attach('business_claims.zip', zip_bytes, 'application/zip')
            email.send()
            
            return HttpResponse(f'Письма отправлены успешно на 2 адреса: edvard88@inbox.ru, 89036414195@mail.ru')
            
        except Exception as e:
            return HttpResponse(f'Ошибка отправки писем: {str(e)}')
    
    return redirect('generate_business_claims')

#=====
import requests
import json
from django.core.mail import send_mail
from django.conf import settings

def send_sms_notification(phone, message):
    """
    Отправка SMS через сервис smsaero.ru
    """
    try:
        # Данные для авторизации в smsaero
        sms_login = os.getenv('SMSAERO_EMAIL')  # Ваш email в smsaero
        sms_api_key = os.getenv('SMSAERO_API_KEY')  # Ваш API ключ
        
        if not sms_login or not sms_api_key:
            print("❌ Не настроены учетные данные SMS сервиса")
            return False
        
        # Формируем базовую авторизацию
        auth = (sms_login, sms_api_key)
        
        # Подготавливаем номер телефона (оставляем только цифры)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone.startswith('8') and len(clean_phone) == 11:
            clean_phone = '7' + clean_phone[1:]  # Преобразуем 8 в 7
        
        # URL для отправки SMS
        url = "https://gate.smsaero.ru/v2/sms/send"
        
        # Данные для отправки
        payload = {
            "number": clean_phone,
            "text": message,
            "sign": "SMS Aero"  # Подпись отправителя (должна быть предварительно настроена в аккаунте)
        }
        
        # Отправляем запрос
        response = requests.post(
            url,
            json=payload,
            auth=auth,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                print(f"✅ SMS отправлено на {phone}")
                return True
            else:
                print(f"❌ Ошибка SMS: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ошибка при отправке SMS: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка отправки SMS: {e}")
        return False

def send_email_notification(email, subject, message):
    """
    Отправка email уведомления
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"✅ Email отправлен на {email}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")
        return False

def send_bulk_notifications(request):
    """
    Массовая рассылка SMS и email всем должникам
    """
    if request.method == 'POST':
        claims_data = request.session.get('all_claims_data', [])
        
        if not claims_data:
            return HttpResponse('Нет данных для рассылки')
        
        # Статистика
        sms_sent = 0
        emails_sent = 0
        total_debtors = len(claims_data)
        
        results = []
        
        for claim in claims_data:
            fio = claim.get('fio', '')
            phone = claim.get('phone', '')
            email_addr = claim.get('email', '')
            debt_amount = claim.get('debt_amount', 0)
            snt_address = claim.get('snt_address', '')
            
            # Пропускаем если нет долга
            if debt_amount <= 0:
                continue
            
            result = {
                'fio': fio,
                'phone': phone,
                'email': email_addr,
                'debt_amount': debt_amount,
                'snt_address': snt_address,
                'sms_sent': False,
                'email_sent': False
            }
            
            # Отправка SMS
            if phone and phone != '_________________________':
                sms_message = f"{fio},задолжен, по {snt_address} в размере {debt_amount:,.2f} руб"
                if send_sms_notification(phone, sms_message):
                    sms_sent += 1
                    result['sms_sent'] = True
            
            # Отправка Email
            if email_addr and email_addr != '_________________________':
                email_subject = f"Уведомление о задолженности - {snt_address}"
                
                email_message = f"""Уважаемый {fio} собственник {snt_address} в КП "Крона"!

Напоминаем вам о важности своевременной оплаты счетов за услуги, предоставляемые ООО «УК ДАР». Оплата счетов должна осуществляться до 10-го числа каждого месяца.

⌛️ Несвоевременная оплата может привести к образованию задолженности, что, в свою очередь, может повлиять на качество и непрерывность предоставления эксплуатационных услуг. 

⚠️ В настоящий момент у вас числится задолженность в размере {debt_amount:,.2f} руб.

🚨Обращаем Ваше внимание, что в соответствии с установленными правилами, при наличии задолженности более одного календарного месяца, собственник можете быть ограничен в предоставлении эксплуатационных услуг, а также отключен от системы дистанционных заказов пропусков Pass 24.online. В указанном случае проезд на территорию будет осуществляется на основании бумажных пропусков, оформленных в порядке, предусмотренном положением об организации въезда и выезда транспортных средств.🚨

📱 Для обсуждения вопросов, связанных с оплатой, вы можете связаться с представителем ООО «УК ДАР» по телефону 8 (915) 173-71-43 (доступен WhatsApp, Telegram, SMS) или по электронной почте: yk.dar@ya.ru.

С уважением,
ООО «УК ДАР»"""
                
                if send_email_notification(email_addr, email_subject, email_message):
                    emails_sent += 1
                    result['email_sent'] = True
            
            results.append(result)
        
        # Сохраняем результаты в сессии
        request.session['notification_results'] = results
        request.session['sms_sent_count'] = sms_sent
        request.session['emails_sent_count'] = emails_sent
        
        context = {
            'total_debtors': total_debtors,
            'sms_sent': sms_sent,
            'emails_sent': emails_sent,
            'results': results,
            'has_results': True
        }
        
        return render(request, 'main/notification_results.html', context)
    
    return redirect('process_business_files')