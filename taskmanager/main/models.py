from django.db import models
from signature_pad import SignaturePadField

# Create your models here.
class LawIssue(models.Model):
    title = models.TextField('Описание')
    signature = SignaturePadField(blank=True, null=True)
    generated_issue = models.TextField('Сгенерированная претензия', default= "Неизвестно", blank=True, null=True)
    
    # signature = CharField(
    #     widget=SignaturePadWidget(attrs={
    #         'width': 500,
    #         'height': 200,
    #         'pen_color': 'blue',
    #         'background_color': 'lightgray',
    #         'clear_button': True,
    #         'save_format': 'image/png',
    #     })
    # )

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Претензия'
        verbose_name_plural = 'Претензии'
