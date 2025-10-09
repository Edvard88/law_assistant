from django.forms import ModelForm, TextInput, Textarea, CharField
from signature_pad import SignaturePadWidget
from ckeditor.widgets import CKEditorWidget

from .models import LawIssue


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
        

