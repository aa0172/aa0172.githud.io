from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_partners, name='search_partners'),
    path('create-session/', views.create_session, name='create_session'),
    path('join-session/<int:session_id>/', views.join_session, name='join_session'),
]