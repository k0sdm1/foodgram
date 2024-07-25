from django.urls import path

from shortlink import views


urlpatterns = [
    path('<link>/', views.reverse_short),
]
