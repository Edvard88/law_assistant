from django.urls import path
from . import views


urlpatterns = [
    #path('', views.create_issue, name = 'home'),
    path('', views.index, name = 'home'),
    path('about', views.about, name = 'about'),
    path('generate-pdf/', views.generate_pdf_xhtml2pdf, name='generate_pdf'),
    path('send-pdf-email/', views.send_pdf_email, name='send_pdf_email'),
    path('download-pdf/', views.download_pdf_only, name='download_pdf'),

    ########
    # Бизнес-маршруты
    path('business/', views.business_dashboard, name='business'),
    path('business/process/', views.process_business_files, name='process_business_files'),
    path('business/generate/', views.generate_business_claims, name='generate_business_claims'),
    path('business/download/', views.download_business_zip, name='download_business_zip'),
    path('business/send-emails/', views.send_business_emails, name='send_business_emails'),
]
