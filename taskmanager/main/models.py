from django.db import models
from signature_pad import SignaturePadField
from ckeditor.fields import RichTextField


# def user_pdf_path(instance, filename):
#     # instance - объект модели, должен иметь связь с User
#     return f'users/{instance.user.username}/pdfs/{filename}'

# Create your models here.
class LawIssue(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    title = models.TextField('Описание')  #!!!!! Переимновать
    generated_issue = RichTextField('Сгенерированная претензия', 
                                       default= "Неизвестно", 
                                       blank=True, 
                                       null=True)
    
    
    #RichTextField(blank=True, null=True) 
    
    signature = SignaturePadField(blank=True, null=True)

    generated_claim_pdf = models.FileField(verbose_name = "Cгенерированный pdf претензии", 
                                           upload_to="data/generated_issue_pdf/",
                                           blank=True)
    
    user_agreement = models.FileField(verbose_name = "Пользовательское соглашение", 
                                      upload_to="data/generated_user_agreement/",
                                      blank=True)
    #user_mail = models.CharField("Mail пользвователя")
     
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Претензия'
        verbose_name_plural = 'Претензии'
