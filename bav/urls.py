from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Actions
    path('actions/', views.action_list, name='action_list'),
    path('actions/create/', views.action_create, name='action_create'),
    path('actions/delete/<int:action_id>/', views.action_delete, name='action_delete'),

    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/update/<int:task_id>/', views.task_update_status, name='task_update_status'),
    path('tasks/delete/<int:task_id>/', views.task_delete, name='task_delete'),

    # Pensee Bete
    path('pensees/', views.pensee_bete_list, name='pensee_bete_list'),
    path('pensees/create/', views.pensee_bete_create, name='pensee_bete_create'),
    path('pensees/delete/<int:pensee_id>/', views.pensee_bete_delete, name='pensee_bete_delete'),

    # Links
    path('links/', views.link_list, name='link_list'),
    path('links/create/', views.link_create, name='link_create'),
    path('links/delete/<int:link_id>/', views.link_delete, name='link_delete'),
]