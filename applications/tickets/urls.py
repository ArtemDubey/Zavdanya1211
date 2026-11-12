from django.urls import path

from applications.tickets import views

urlpatterns = [
    path('', views.ticket_list_view, name='ticket_list'),
    path('create/', views.ticket_create_view, name='ticket_create'),
    path('<int:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
    path('<int:ticket_id>/take/', views.ticket_take_view, name='ticket_take'),
    path('<int:ticket_id>/status/', views.ticket_status_view, name='ticket_status'),
    path('<int:ticket_id>/priority/', views.ticket_priority_view, name='ticket_priority'),
    path('<int:ticket_id>/assign/', views.ticket_assign_view, name='ticket_assign'),
]