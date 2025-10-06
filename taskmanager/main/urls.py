from django.urls import path
from . import views


urlpatterns = [
    #path('', views.create_issue, name = 'home'),
    path('', views.index, name = 'home'),
    path('about', views.about, name = 'about'),
    path('generate-pdf/', views.generate_pdf_xhtml2pdf, name='generate_pdf'),
    path('send-pdf-email/', views.send_pdf_email, name='send_pdf_email'),
    path('download-pdf/', views.download_pdf_only, name='download_pdf'),
    path('test-pdf/', views.test_pdf_generation, name='test_pdf'),
]

