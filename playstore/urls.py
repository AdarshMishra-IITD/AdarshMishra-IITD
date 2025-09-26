from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('app/<int:app_id>/', views.app_detail, name='app_detail'),
    path('app/<int:app_id>/add_review/', views.add_review, name='add_review'),
    path('supervisor/reviews/', views.supervisor_reviews, name='supervisor_reviews'),
    path('supervisor/review/<int:review_id>/approve/', views.approve_review, name='approve_review'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/profile/', views.profile, name='profile'),
]
