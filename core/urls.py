from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.mailing_list, name='mailing_list'),
    path('<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/update/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('<int:pk>/start/', views.start_mailing, name='start_mailing'),
    path('stats/', views.user_stats, name='user_stats'),
]