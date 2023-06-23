from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('select-game', views.select_game, name='select-game'),
    path('search', views.filter, name='search'),
    path('view', views.view, name='view'),
    path('resolve', views.resolve, name='resolve'),
    path('delete', views.delete, name='delete'),
    path('copy', views.copy, name='copy'),
    path('new-game', views.new_game, name='new-game'),
    path('delete-game', views.delete_game, name='delete-game'),
    path('make', views.make_object, name='make'),
    path('modify', views.modify_object, name='modify'),
]
