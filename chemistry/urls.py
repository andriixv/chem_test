from django.urls import path

from django.conf import settings 
from django.conf.urls.static import static

from . import views

app_name = 'chemistry'
urlpatterns = [
    # домашня
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('generator', views.generator, name='generator'),
    path('edit_question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('add_question/', views.add_question, name='add_question'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)