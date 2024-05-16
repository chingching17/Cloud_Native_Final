from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('history', views.show_history, name="show_history"),
    path('add', views.add, name='add'),
    path('add_order/', views.add_order, name='add_order'),
]