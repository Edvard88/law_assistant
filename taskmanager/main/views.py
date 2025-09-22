from django.shortcuts import render, redirect
# from .models import Task
# from .forms import TaskForm
# Create your views here.
from .models import LawIssue
from .forms import LawIssueForm
from .llm_model import model_predict


def index(request):
    return render(request, 'main/index.html')

def about(request):
    return render(request, 'main/about.html')


# def create(request):
#     error = ''
#     if request.method == 'POST':
#         form = TaskForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#         else:
#             error = 'Форма была неверной'

#     form = TaskForm()
#     context = {
#         'form': form,
#         'error': error
#     }
#     return render(request, 'main/create.html', context)




def create_issue(request):
    #reversed_text = "Тест"
    error = ''
    if request.method == 'POST':
        form = LawIssueForm(request.POST)
        print("form.is_valid()", form.is_valid())
        if form.is_valid():

            generated_issue = model_predict(form.cleaned_data['title'])
            #reversed_text = model_predict(form.cleaned_data['title'])
    
            # Сохраняем без коммита в БД
            instance = form.save(commit=False)
            instance.generated_issue = generated_issue
            instance.save()
            
            # Обновляем форму с instance
            form = LawIssueForm(instance=instance)
            
            pass
        else:
            error = 'Форма была неверной'


    form = LawIssueForm()
    #law_issue = LawIssue()
    
    context = {
        'form': form,
        'error': error,
        #'reversed_text' : reversed_text,
        #'pedict_answer': pedict_answer
        #'predict': generated_issue_predict
        #'signature_data' : signature_data,
        #'data': form.cleaned_data
    }
    return render(request, 'main/create_issue.html', context)



def reverse_view(request):
    reversed_text = None
    if request.method == "POST":
        form = LawIssueForm(request.POST)
        if form.is_valid():
            reversed_text = "Тест"

            generated_issue = model_predict(form.cleaned_data['title'])
            reversed_text = model_predict(form.cleaned_data['title'])
    
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
        'show_generated_issue': False
        #'generated_issue': generated_text
    }
    return render(request, "main/create_issue.html", context)



from django.http import HttpResponse
from django.template.loader import render_to_string
#from weasyprint import HTML

from django.template.loader import get_template
from xhtml2pdf import pisa


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
