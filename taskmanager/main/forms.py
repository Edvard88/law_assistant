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
                'placeholder' : """Напишите на обычном языке вышу претензию указав ваше ФИО, а также ФИО к кому претензаия или название компании.\n Мы сгенерим корректный текст претензии"""

            }),
            "generated_issue": CKEditorWidget(attrs={
                'class': 'form-control',
                'style': 'width: 100%; height: 1000;'
                
            }),

            "signature": SignaturePadWidget(attrs={
                'style': 'width: 500px; height: 200px; border: 2px solid #ccc; background-color: lightgray;'
            })

    #         "signature" : CharField(
    #     widget=SignaturePadWidget(attrs={
    #         'width': 500,
    #         'height': 200,
    #         'pen_color': 'blue',
    #         'background_color': 'lightgray',
    #         'clear_button': True,
    #         'save_format': 'image/png',
    #     })
    # )
        #     "signature":
        #         SignaturePadWidget(attrs={
        #             # 'dotSize':2.5,
        #             # 'inWidth': 1.0,
        #             # 'maxWidth': 4.0,
        #             # 'backgroundColor': "rgb(240, 240, 240)",
        #             # 'penColor': "rgb(0, 0, 255)"

        #             # 'data-dot-size': '2.5',
        #             # 'data-min-width': '1.0',
        #             # 'data-max-width': '4.0',
        #             # 'style': 'background-color: rgb(0, 0, 255); border: 1px solid #ccc; width: 100%; height: 200px;',
        #             # 'class': 'signature-pad-wrapper'

        #         # 'class': 'signature-pad-wrapper',
        #         # 'style': 'width: 100%; height: 200px; border: 1px solid #ccc; background-color: rgb(0, 0, 255);'
        # }),   
        }
    
    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     # Обработка custom_signature если нужно
    #     if commit:
    #         instance.save()
    #     return instance



