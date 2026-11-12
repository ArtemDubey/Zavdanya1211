from django.urls import path

from applications.manageboard import views

urlpatterns = [
    path('', views.dashboard_view, name='manage_dashboard'),
    path('users/', views.users_view, name='manage_users'),
    path('users/<int:user_id>/role/', views.user_role_view, name='manage_user_role'),
    path('categories/', views.categories_view, name='manage_categories'),
    path('categories/create/', views.category_create_view, name='manage_category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit_view, name='manage_category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete_view, name='manage_category_delete'),
]