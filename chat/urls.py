from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_rooms, name='chat_rooms'),
    path('<str:district>/<str:interest>/', views.chat_room, name='chat_room'),
    path('leave/<int:room_id>/', views.leave_chat, name='leave_chat'),
    path('api/messages/<int:room_id>/', views.get_messages, name='get_messages'),
]