from django.db import models
from signature_pad import SignaturePadField
from ckeditor.fields import RichTextField


def generated_issue_pdf_path(instance, filename):
    """Путь для сохранения сгенерированных претензий"""
    return f'data/generated_issue_pdf/{filename}'

def user_agreement_pdf_path(instance, filename):
    """Путь для сохранения пользовательских соглашений"""
    return f'data/generated_user_agreement/{filename}'

# Create your models here.
class LawIssue(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    title = models.TextField('Описание')  #!!!!! Переимновать
    generated_issue = RichTextField('Сгенерированная претензия', 
                                       default= "Неизвестно", 
                                       blank=True, 
                                       null=True)
    
    
    signature = SignaturePadField(blank=True, null=True)

    generated_claim_pdf = models.FileField(verbose_name = "Cгенерированный pdf претензии", 
                                           upload_to=generated_issue_pdf_path,
                                           blank=True)
    
    user_agreement = models.FileField(verbose_name = "Пользовательское соглашение", 
                                      upload_to=user_agreement_pdf_path,
                                      blank=True)
    
    # Добавленные поля для контактных данных пользователя
    user_mail = models.EmailField("Email пользователя", max_length=255, blank=True, null=True)
    user_tel = models.CharField("Телефон пользователя", max_length=20, blank=True, null=True)
     

     
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Претензия'
        verbose_name_plural = 'Претензии'


class BusinessClient(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    client_name = models.CharField("Название организации", max_length=255, blank=True, null=True)
    # client_inn = models.CharField("ИНН", max_length=20, blank=True, null=True)
    # client_ogrn = models.CharField("ОГРН", max_length=20, blank=True, null=True)
    # client_address = models.TextField("Адрес", blank=True, null=True)
    # client_email = models.EmailField("Email", max_length=255, blank=True, null=True)
    # client_phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    
    # Файлы
    charges_file = models.FileField(
        "Файл начислений и оплат", 
        upload_to='business/charges/',
        blank=True,
        null=True
    )
    personal_data_claim_file = models.FileField(
        "Претензия персональные данные", 
        upload_to='business/personal_data/',
        blank=True,
        null=True
    )
    snt_claim_file = models.FileField(
        "Претензия СНТ", 
        upload_to='business/snt/',
        blank=True,
        null=True
    )
    
    # Сгенерированные PDF
    generated_pdf = models.FileField(
        "Сгенерированный PDF", 
        upload_to='business/generated_pdf/',
        blank=True,
        null=True
    )
    
    # ZIP архив
    zip_archive = models.FileField(
        "ZIP архив", 
        upload_to='business/zips/',
        blank=True,
        null=True
    )
    
    is_processed = models.BooleanField("Обработан", default=False)
    
    def __str__(self):
        return f"{self.client_name} ({self.client_inn})"
    
    class Meta:
        verbose_name = 'Бизнес-клиент'
        verbose_name_plural = 'Бизнес-клиенты'

class NotificationCampaign(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    campaign_name = models.CharField("Название рассылки", max_length=255, blank=True)
    total_debtors = models.IntegerField("Всего должников", default=0)
    sms_sent = models.IntegerField("SMS отправлено", default=0)
    emails_sent = models.IntegerField("Email отправлено", default=0)
    status = models.CharField("Статус", max_length=50, default='processing')
    
    def __str__(self):
        return f"Рассылка от {self.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

class NotificationResult(models.Model):
    campaign = models.ForeignKey(NotificationCampaign, on_delete=models.CASCADE, related_name='results')
    fio = models.CharField("ФИО", max_length=255)
    snt_address = models.CharField("Адрес СНТ", max_length=255)
    debt_amount = models.DecimalField("Сумма долга", max_digits=12, decimal_places=2)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.CharField("Email", max_length=255, blank=True)
    sms_sent = models.BooleanField("SMS отправлено", default=False)
    email_sent = models.BooleanField("Email отправлено", default=False)
    sent_at = models.DateTimeField("Отправлено", auto_now_add=True)
    
    class Meta:
        verbose_name = 'Результат рассылки'
        verbose_name_plural = 'Результаты рассылки'
