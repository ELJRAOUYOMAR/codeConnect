from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('problem/<int:pk>/', views.problem_detail, name='problem_detail'),
    path('problem/new/', views.create_problem, name='create_problem'),
    path('problem/<int:pk>/solution/', views.add_solution, name='add_solution'),
    path('search/', views.search_problems, name='search_problems'),
    path('logout/', views.logout_view, name='logout'),
]