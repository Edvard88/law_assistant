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




def index(request):
    # Обработка GET запроса - показываем пустую форму
    if request.method != 'POST':
        form = LawIssueForm()
        context = {
            'form': form,
            'show_generated_issue': False,
            'show_signature': False,
            'current_step': 1  # Добавляем отслеживание текущего шага
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
    
    if title:
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
            # Шаг 4: Все данные есть - можно генерировать PDF
            instance = form.save()
            show_generated_issue = True
            show_signature = True
            current_step = 4
    else:
        # Шаг 1: Нет title
        current_step = 1
        show_generated_issue = False
        show_signature = False
    
    context = {
        'form': form,
        'show_generated_issue': show_generated_issue,
        'show_signature': show_signature,
        'current_step': current_step
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

def generate_claim_pdf_context(claim_text, generated_issue_text):
    """Генерирует контекст для PDF претензии"""
    return {
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
        'generated_issue_text': generated_issue_text,
    }

def generate_agreement_pdf_context(claim_text):
    """Генерирует контекст для PDF пользовательского соглашения"""
    return {
        'from_whom': model_from_whom(claim_text),
        'from_whom_ogrn': model_from_whom_ogrn(claim_text),
        'from_whom_inn': model_from_whom_inn(claim_text),
        'from_whom_address': model_from_whom_address(claim_text),
    }

def send_pdf_email(request):
    """Отправляет PDF файлы на email и сохраняет их в папки проекта"""
    if request.method == 'POST':
        user_email = request.POST.get('user_email')
        user_agreement = request.POST.get('user_agreement')
        title = request.POST.get('title')
        generated_issue = request.POST.get('generated_issue')
        signature = request.POST.get('signature')
        
        if not user_agreement:
            return HttpResponse('Необходимо согласие с пользовательским соглашением')
        
        try:
            # Генерируем PDF претензии
            claim_context = generate_claim_pdf_context(title, generated_issue)
            claim_html = render_to_string('main/pdf_template.html', claim_context)
            claim_pdf = generate_pdf_from_html(claim_html)
            
            # Генерируем PDF пользовательского соглашения
            agreement_context = generate_agreement_pdf_context(title)
            agreement_html = render_to_string('main/user_agreement.html', agreement_context)
            agreement_pdf = generate_pdf_from_html(agreement_html)
            
            if not claim_pdf or not agreement_pdf:
                return HttpResponse('Ошибка генерации PDF')
            
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
            claim_saved = save_pdf_to_file(claim_pdf, claim_filepath)
            agreement_saved = save_pdf_to_file(agreement_pdf, agreement_filepath)
            
            if not claim_saved or not agreement_saved:
                return HttpResponse('Ошибка сохранения PDF файлов')
            
            # Сбрасываем позицию в файлах для отправки по email
            claim_pdf.seek(0)
            agreement_pdf.seek(0)
            
            # Создаем email
            subject = 'Ваша претензия - AI Law Assistant'
            body = f"""
            Уважаемый пользователь,
            
            Во вложении вы найдете:
            1. Сгенерированную претензию
            2. Пользовательское соглашение
            
            Файлы также сохранены в нашей системе.
            
            С уважением,
            AI Law Assistant
            """
            
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
                cc=['admin@mail.ru', 'edvard88@mail.ru']  # Копии на системные почты
            )
            
            # Прикрепляем PDF файлы
            email.attach('претензия.pdf', claim_pdf.read(), 'application/pdf')
            email.attach('пользовательское_соглашение.pdf', agreement_pdf.read(), 'application/pdf')
            
            # Отправляем email
            email.send()
            
            # Сохраняем в модель LawIssue
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
            
            success_message = f"""
            PDF успешно отправлен на вашу почту {user_email}!
            
            Файлы также сохранены:
            - Претензия: {claim_filepath}
            - Пользовательское соглашение: {agreement_filepath}
            """
            
            return HttpResponse(success_message)
            
        except Exception as e:
            return HttpResponse(f'Ошибка отправки: {str(e)}')
    
    return redirect('home')

def generate_pdf_xhtml2pdf(request):
    """Генерирует PDF для скачивания и сохраняет в папку"""
    if request.method == 'POST':
        title = request.POST.get('title')
        generated_issue = request.POST.get('generated_issue')
        
        context = generate_claim_pdf_context(title, generated_issue)
        html = render_to_string('main/pdf_template.html', context)
        
        # Генерируем PDF
        pdf_file = generate_pdf_from_html(html)
        
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
        
        # Генерируем PDF претензии
        claim_context = generate_claim_pdf_context(title, generated_issue)
        claim_html = render_to_string('main/pdf_template.html', claim_context)
        claim_pdf = generate_pdf_from_html(claim_html)
        
        # Генерируем PDF пользовательского соглашения
        agreement_context = generate_agreement_pdf_context(title)
        agreement_html = render_to_string('main/user_agreement.html', agreement_context)
        agreement_pdf = generate_pdf_from_html(agreement_html)
        
        if not claim_pdf or not agreement_pdf:
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
                signature=request.POST.get('signature', '')
            )
            
            with open(claim_filepath, 'rb') as claim_file:
                law_issue.generated_claim_pdf.save(claim_filename, claim_file)
            
            with open(agreement_filepath, 'rb') as agreement_file:
                law_issue.user_agreement.save(agreement_filename, agreement_file)
            
            return response
        else:
            return HttpResponse('Ошибка сохранения PDF файлов')
    
    return redirect('home')