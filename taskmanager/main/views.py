from django.shortcuts import render, redirect

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
    """Генерирует PDF из HTML контента"""
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    
    if pisa_status.err:
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
    """Отправляет PDF файлы на email"""
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
            
            # Создаем email
            subject = 'Ваша претензия - AI Law Assistant'
            body = f"""
            Уважаемый пользователь,
            
            Во вложении вы найдете:
            1. Сгенерированную претензию
            2. Пользовательское соглашение
            
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
            
            # Сохраняем в модель (опционально)
            law_issue = LawIssue.objects.create(
                title=title,
                generated_issue=generated_issue,
                signature=signature
            )
            law_issue.user_agreement.save('user_agreement.pdf', agreement_pdf)
            law_issue.generated_claim_pdf.save('claim.pdf', claim_pdf)
            
            return HttpResponse('PDF успешно отправлен на вашу почту!')
            
        except Exception as e:
            return HttpResponse(f'Ошибка отправки: {str(e)}')
    
    return redirect('home')

def generate_pdf_xhtml2pdf(request):
    """Генерирует PDF для скачивания"""
    if request.method == 'POST':
        title = request.POST.get('title')
        generated_issue = request.POST.get('generated_issue')
        
        context = generate_claim_pdf_context(title, generated_issue)
        html = render_to_string('main/pdf_template.html', context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="претензия.pdf"'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        if pisa_status.err:
            return HttpResponse('Ошибка генерации PDF')
        return response
    
    return redirect('home')