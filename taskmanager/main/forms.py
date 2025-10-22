from django.forms import ModelForm, TextInput, Textarea, CharField
from signature_pad import SignaturePadWidget
from ckeditor.widgets import CKEditorWidget

from .models import LawIssue, BusinessClient


class LawIssueForm(ModelForm):

    class Meta:
        model = LawIssue
        fields = ["title", "signature", "generated_issue"] 
        widgets = {
            "title": Textarea(attrs={
            'class': 'form-control',
            'placeholder': """Пишите здесь:

Пример: "Я, Иванов Иван Иванович, проживающий по адресу г. Москва, ул. Ленина, д. 1, кв. 1, 
имею претензию к ООО 'Ромашка' по адресу г. Москва, ул. Пушкина, д. 2...""",
            'rows': '10',  # Увеличиваем количество строк
            'style': 'height: 300px; min-height: 300px; resize: vertical;'  # Фиксируем высоту и разрешаем изменение
        }),
            "generated_issue": CKEditorWidget(attrs={
                'class': 'form-control',
                'style': 'width: 100%; height: 1000;'
                
            }),

            "signature": SignaturePadWidget(attrs={
                'style': 'width: 500px; height: 200px; border: 2px solid #ccc; background-color: lightgray;',
            }),

            "user_mail": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.ru'
            }),
            
            "user_tel": TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (XXX) XXX-XX-XX'
            })
   }
        

class BusinessClientForm(ModelForm):
    class Meta:
        model = BusinessClient
        fields = [
            'client_name', 
            # 'client_inn', 'client_ogrn', 'client_address',
            # 'client_email', 'client_phone', 
            'charges_file', 
            'personal_data_claim_file', 'snt_claim_file'
        ]
        widgets = {
            'client_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ООО "Ромашка"'
            # }),
            # 'client_inn': TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '1234567890'
            # }),
            # 'client_ogrn': TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '1234567890123'
            # }),
            # 'client_address': Textarea(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'г. Москва, ул. Ленина, д. 1',
            #     'rows': 3
            # }),
            # 'client_email': TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'example@company.ru'
            # }),
            # 'client_phone': TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': '+7 (XXX) XXX-XX-XX'
            }),
        }

