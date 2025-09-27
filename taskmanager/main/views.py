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

def generate_issue_text(claim_text):
    generated_issue = model_predict(claim_text)
    return generated_issue


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

def generate_pdf(request):
    # Эта функция остается отдельной для генерации PDF
    if request.method == 'POST':
        # Логика генерации PDF
        pass
    
# def create_issue(request):
#     #!!!!!! отдельные функции  generated_issue, signature_data

#     # def generated_issue(request.POST.title):
#     #     return  text_generated_issue
    

#     #ДЗ
#     # 1) Поправить модель поля
#     # 2) Разбить функцию create_issue на подфункции и отобразить на одном url
#     # 3) Добавить функции 2 pdf и отправку
    
#     #reversed_text = "Тест"
#     error = ''
#     if request.method == 'POST':
#         form = LawIssueForm(request.POST)
#         print("form.is_valid()", form.is_valid())
#         print("!!!!!!!!!!!!request.POST.title",request.POST.title)
#         if form.is_valid():
#             data = form.cleaned_data

#             if data['title']:
#                 generated_issue = generate_issue_text(form.cleaned_data['title'])
    
#                 # Сохраняем без коммита в БД
#                 instance = form.save(commit=False)
#                 instance.generated_issue = generated_issue
#                 instance.save()

#                 # Восстанавливаем ВСЕ поля из исходной формы
#                 for field, value in data.items():
#                     if hasattr(instance, field):
#                         setattr(instance, field, value)
#                 # Сохраняем окончательно
#                 instance.save()
            
#                 # Обновляем форму с instance
#                 form = LawIssueForm(instance=instance)
                
#                 context = {
#                     'form': form,
#                     'show_generated_issue': True
#                 }
#                 return render(request, "main/create_issue.html", context)
#             else:
#                 context = {
#                     'form': form,
#                     'show_generated_issue': False
#                 }
#                 return render(request, "main/create_issue.html", context)
#         else:
#             error = 'Форма была неверной'
#             context = {'form': form,
#                     'error': error}
#             return render(request, "main/create_issue.html", context)
    
    

#     form = LawIssueForm()
#     #law_issue = LawIssue()
    
#     context = {
#         'form': form,
#         'error': error,
#         #'reversed_text' : reversed_text,
#         #'pedict_answer': pedict_answer
#         #'predict': generated_issue_predict
#         #'signature_data' : signature_data,
#         #'data': form.cleaned_data
#     }
#     return render(request, 'main/create_issue.html', context)



def reverse_view(request):
    reversed_text = None
    if request.method == "POST":
        form = LawIssueForm(request.POST)
        if form.is_valid():
            reversed_text = "Тест"

            generated_issue = model_predict(form.cleaned_data['title'])
            #reversed_text = model_predict(form.cleaned_data['title'])
    
            # Сохраняем без коммита в БД
            instance = form.save(commit=False)
            instance.generated_issue = generated_issue
            instance.save()
            
            # Обновляем форму с instance
            form = LawIssueForm(instance=instance)

            context = {
                'form': form,
                # 'error': error,
                'reversed_text' : reversed_text,
                'show_generated_issue': True
            }
            return render(request, "main/create_issue.html", context)
     
    else:
        form = LawIssueForm()
    context = {
        'form': form,   
        # 'error': error,
        'reversed_text' : reversed_text,
        'show_generated_issue': False,
        #'generated_issue': generated_issue
    }
    return render(request, "main/create_issue.html", context)





def generate_pdf_xhtml2pdf(request):
    if request.method == 'POST':
        form = LawIssueForm(request.POST)
        print(f"!!!!POST data: {request.POST}")  # Что пришло в запросе
        if form.is_valid():
            print(f"!!!!Form is valid: {form.is_valid()}")  # Добавьте эту строку для отладки
            print(f"!!!!Form errors: {form.errors}")  # И эту
            template_path = 'pdf_template.html'
            context = {'form': form.cleaned_data}
            print(f"!!!!Form data: {form.cleaned_data}")  # Отладочная информация
            
            # Рендерим шаблон
            template = get_template(template_path)
            html = template.render(context)
            
            # Создаем PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="form_data.pdf"'
            
            # Конвертируем HTML в PDF
            pisa_status = pisa.CreatePDF(html, dest=response)
            
            if pisa_status.err:
                return HttpResponse('Ошибка генерации PDF')
            return response
    
    else:
        form = LawIssueForm()
    
    return render(request, 'main/pdf_template.html', {'form': form})
        

# !!!!!!def pdf_второй

#!!!!!!! def отправку_на_почту




#===========


# def create_issue(request):
#     #!!!!!! отдельные функции  generated_issue, signature_data

#     # def generated_issue(request.POST.title):
#     #     return  text_generated_issue
    

#     #ДЗ
#     # 1) Поправить модель поля
#     # 2) Разбить функцию create_issue на подфункции и отобразить на одном url
#     # 3) Добавить функции 2 pdf и отправку
    
#     #reversed_text = "Тест"
#     error = ''
#     if request.method == 'POST':
#         form = LawIssueForm(request.POST)
#         print("form.is_valid()", form.is_valid())
#         if form.is_valid():

#             generated_issue = model_predict(form.cleaned_data['title'])
#             #reversed_text = model_predict(form.cleaned_data['title'])
    
#             # Сохраняем без коммита в БД
#             instance = form.save(commit=False)
#             instance.generated_issue = generated_issue
#             instance.save()
            
#             # Обновляем форму с instance
#             form = LawIssueForm(instance=instance)
            
            
#             pass
#         else:
#             error = 'Форма была неверной'

#     form = LawIssueForm()
#     #law_issue = LawIssue()
    
#     context = {
#         'form': form,
#         'error': error,
#         #'reversed_text' : reversed_text,
#         #'pedict_answer': pedict_answer
#         #'predict': generated_issue_predict
#         #'signature_data' : signature_data,
#         #'data': form.cleaned_data
#     }
#     return render(request, 'main/create_issue.html', context)



#============

# def create_issue(request):
#     #reversed_text = "Тест"
#     error = ''
#     if request.method == 'POST':
#         form = LawIssueForm(request.POST)
#         print("form.is_valid()", form.is_valid())
#         if form.is_valid():

#             generated_issue = model_predict(form.cleaned_data['title'])
#             #reversed_text = model_predict(form.cleaned_data['title'])
    
#             # Сохраняем без коммита в БД
#             instance = form.save(commit=False)
#             instance.generated_issue = generated_issue
#             instance.save()
            
#             # Обновляем форму с instance
#             form = LawIssueForm(instance=instance)
            
            
#             pass
#         else:
#             error = 'Форма была неверной'


#     form = LawIssueForm()
#     #law_issue = LawIssue()
    
#     context = {
#         'form': form,
#         'error': error,
#         #'reversed_text' : reversed_text,
#         #'pedict_answer': pedict_answer
#         #'predict': generated_issue_predict
#         #'signature_data' : signature_data,
#         #'data': form.cleaned_data
#     }
#     return render(request, 'main/create_issue.html', context)





#============

# def model_predict(text):
#     return text[::-1] 


# def create_issue(request):
#     error = ''
#     if request.method == 'POST':
#         form = LawIssueForm(request.POST)
#         if form.is_valid():
#             #form.save()
#             #return redirect('home')
#             #signature_data = form.cleaned_data['signature']
#             #if signature_data:
#                 # Преобразуем данные подписи в изображение (PNG)
#             pass
#         else:
#             error = 'Форма была неверной'


#     form = LawIssueForm()
#     #law_issue = LawIssue()
    
#     context = {
#         'form': form,
#         'error': error,
#         #'signature_data' : signature_data,
#         #'data': form.cleaned_data
#     }
#     return render(request, 'main/create_issue.html', context)



# def reverse_view(request):
#     reversed_text = None
#     if request.method == "POST":
#         form = LawIssueForm(request.POST)
#         if form.is_valid():
#             text = form.cleaned_data['title'] 
#             print("form!!!", form)
#             reversed_text = model_predict(text)  # переворот строки
#     else:
#         form = LawIssueForm()


#     context = {
#         'form': form,
#         # 'error': error,
#         'reversed_text' : reversed_text,
#     }
#     return render(request, "main/create_issue.html", context)
