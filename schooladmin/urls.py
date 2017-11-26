from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^users/$', views.users_list, name='users_list'),
    url(r'^users/create', views.user_create, name="user_create"),
    url(r'^users/(?P<user_id>[0-9]+)/edit', views.user_edit, name="user_edit"),
    url(r'^lesson_records/$', views.lesson_records, name='lesson_records'),
    url(r'^lesson_records/create', views.lesson_record_create, name='lesson_record_create'),
    url(r'^lesson_records/(?P<lesson_record_id>[0-9]+)/edit', views.lesson_record_edit, name='lesson_record_edit'),
    url(r'^invoices/$', views.invoices_list, name='invoices_list'),
    url(r'^reports/$', views.reports, name='reports'),
]
