from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create API router
router = DefaultRouter()

app_name = 'chatbot'

urlpatterns = [
    # Main chatbot interface
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('faqs/', views.faqs, name='faqs'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/ask/', views.ask_question, name='api_ask'),
    path('api/health/', views.health_check, name='api_health'),
    path('api/faqs/', views.get_faqs, name='api_faqs'),
]
