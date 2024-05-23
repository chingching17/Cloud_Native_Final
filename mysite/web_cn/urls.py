from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('history', views.show_history, name="show_history"),
    path('add', views.add, name='add'),
    path('manage', views.manage, name='manage'),

    path('add_order/', views.add_order, name='add_order'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('logs/', views.view_logs, name='view_logs'),
]