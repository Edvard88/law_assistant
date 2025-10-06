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
from .llm_model import model_predict, \
                        model_to_whom, model_to_whom_address, model_to_whom_ogrn, model_to_whom_inn, model_to_whom_mail, model_to_whom_tel, \
                        model_from_whom, model_from_whom_address, model_from_whom_ogrn, model_from_whom_inn, model_from_whom_mail, model_from_whom_tel

from django.http import HttpResponse
from django.template.loader import render_to_string
#from weasyprint import HTML

from django.template.loader import get_template
from xhtml2pdf import pisa


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
    
    # Создаем контекст для шаблона
    context = {
        'to_whom': model_to_whom(claim_text),
        'to_whom_address': model_to_whom_address(claim_text),
        'to_whom_ogrn': model_to_whom_ogrn(claim_text),
        'to_whom_inn': model_to_whom_inn(claim_text),
        'to_whom_mail': model_to_whom_mail(claim_text),
        'to_whom_tel': model_to_whom_tel(claim_text),
        'from_whom': model_from_whom(claim_text),
        'from_whom_address': model_from_whom_address(claim_text),
        'from_whom_ogrn': model_from_whom_ogrn(claim_text),
        'from_whom_inn': model_from_whom_inn(claim_text),
        'from_whom_mail': model_from_whom_mail(claim_text),
        'from_whom_tel': model_from_whom_tel(claim_text),
        'generated_issue_text': generated_issue,
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

            # Генерируем PDF претензии с подписью
            logger.info("Generating claim PDF...")
            claim_context = generate_claim_pdf_context(title, generated_issue, signature)
            claim_html = render_to_string('main/pdf_template.html', claim_context)
            #claim_html = render_to_string('main/pdf_template_simple.html', claim_context)
            #claim_pdf = generate_pdf_from_html(claim_html)
            claim_pdf = generate_pdf_weasyprint(claim_html)
            
            # Генерируем PDF пользовательского соглашения
            logger.info("Generating agreement PDF...")
            agreement_context = generate_agreement_pdf_context(title, signature)
            agreement_html = render_to_string('main/user_agreement.html', agreement_context)
            #agreement_pdf = generate_pdf_from_html(agreement_html)
            agreement_pdf = generate_pdf_weasyprint(agreement_html)


            # #####
            #             # ===== ДОБАВЬТЕ ЗДЕСЬ ПРОВЕРКУ ДАННЫХ =====
            # logger.info("=== CHECKING TEMPLATE DATA ===")
            # logger.info(f"to_whom: {claim_context.get('to_whom')}")
            # logger.info(f"from_whom: {claim_context.get('from_whom')}")
            # logger.info(f"to_whom_address: {claim_context.get('to_whom_address')}")
            # logger.info(f"from_whom_address: {claim_context.get('from_whom_address')}")
            # logger.info(f"generated_issue_text sample: {str(claim_context.get('generated_issue_text', ''))[:200]}")
            
            # # Проверим сырой HTML до рендеринга
            # test_html = "<html><body><p>Тестовый русский текст: Проверка кодировки</p></body></html>"
            # test_pdf = generate_pdf_from_html(test_html)
            # if test_pdf:
            #     logger.info("✓ Simple test HTML works - кодировка в порядке")
            # else:
            #     logger.info("✗ Simple test HTML fails - проблема с генерацией")
            
            # # Проверим вывод моделей
            # logger.info("=== CHECKING MODEL OUTPUTS ===")
            # logger.info(f"model_to_whom: {model_to_whom(title)}")
            # logger.info(f"model_from_whom: {model_from_whom(title)}")
            # # ===== КОНЕЦ ПРОВЕРКИ ДАННЫХ =====

            # #####
            
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
            if 'admin@mail.ru':  # Добавляем CC только если указан
                msg['Cc'] = 'admin@mail.ru'
            
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
            
            # Формируем список получателей
            recipients = [user_email]
            if 'admin@mail.ru':
                recipients.append('admin@mail.ru')
            
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
            
            success_message = f"""
            PDF успешно отправлен на вашу почту {user_email}!
            
            Проверьте:
            1. Папку "Входящие"
            2. Папку "Спам" 
            3. Папку "Отправленные" в {settings.EMAIL_HOST_USER}
            
            Файлы также сохранены на сервере:
            - Претензия: {claim_filepath}
            - Пользовательское соглашение: {agreement_filepath}
            """
            
            logger.info("=== send_pdf_email completed successfully ===")
            return HttpResponse(success_message)
            
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

def test_pdf_generation(request):
    """Тестовая функция для проверки PDF"""

    
    
    # Простейший HTML с русским текстом
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; font-size: 14px; }
        </style>
    </head>
    <body>
        <h1>Тестовый документ</h1>
        <p>Это тестовый текст на русском языке.</p>
        <p>Кириллица: АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ</p>
        <p>абвгдеёжзийклмнопрстуфхцчшщъыьэюя</p>
    </body>
    </html>
    """
    
    try:
        pdf_file = io.BytesIO()
        HTML(string=test_html, encoding='utf-8').write_pdf(pdf_file)
        pdf_file.seek(0)
        
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="test.pdf"'
        return response
    except Exception as e:
        return HttpResponse(f"Error: {e}")

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
        
        print("=== DEBUG final_html ===")
        print("Content (last 500 chars):")
        print(final_html[-500:] if final_html else "EMPTY")
        print("=== END DEBUG ===")
        
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