from django.urls import path,re_path
from diamondsapp import views

urlpatterns = [
		path("", views.home)
]