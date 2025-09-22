from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = 'home'),
    path('about', views.about, name = 'about'),
    path('create', views.create, name = 'create'),
    path('create_issue', views.create_issue, name = 'create_issue'), 
    path("reverse", views.reverse_view, name="reverse"),
    path('generate_pdf', views.generate_pdf_xhtml2pdf, name='generate_pdf'),
]

