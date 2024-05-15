from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('history', views.show_history, name="show_history"),
]