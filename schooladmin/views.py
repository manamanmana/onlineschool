from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .services import (
    get_all_users, 
    add_a_user,
    get_a_user,
    update_a_user,
    get_all_lesson_records,
    add_a_lesson_record,
    get_a_lesson_record,
    update_a_lesson_record,
    get_invoice_for_month,
    get_sales_report_by_genre_sex_for_month,
    get_sales_report_by_genre_sex_age_for_month,
)
from .forms import UserForm, LessonRecordForm, GenericMonthPickerForm
from datetime import date

# Create your views here.
def index(request):
    return render(request, 'schooladmin/index.html', {})

def users_list(request):
    users = get_all_users()
    return render(request, 'schooladmin/users_list.html', {'users': users})

def user_edit(request, user_id=""):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            # Process user update
            modified_user_data = user_form.cleaned_data
            update_a_user(user_id, modified_user_data)
            return HttpResponseRedirect('/schooladmin/users/')
    else:
        modifled_user = get_a_user(user_id)
        modified_user_data = {
            'name': modifled_user.name,
            'sex': modifled_user.sex,
            'age': modifled_user.age,
        }
        user_form = UserForm(modified_user_data)

    context = {'form': user_form, 'user_id': user_id}
    return render(request, 'schooladmin/user_edit.html', context)


def user_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            # Process user addition
            new_user_data = user_form.cleaned_data
            add_a_user(new_user_data)
            return HttpResponseRedirect('/schooladmin/users/')
    else:
        user_form = UserForm()

    return render(request, 'schooladmin/user_create.html', {'form': user_form})

def lesson_records(request):
    records = get_all_lesson_records()
    return render(request, 'schooladmin/lesson_records.html', {'records': records})

def lesson_record_create(request):
    if request.method == 'POST':
        record_form = LessonRecordForm(request.POST)
        if record_form.is_valid():
            # Process record addition
            new_record_data = record_form.cleaned_data
            add_a_lesson_record(new_record_data)
            return HttpResponseRedirect('/schooladmin/lesson_records/')
    else:
        record_form = LessonRecordForm()

    return render(request, 'schooladmin/lesson_record_create.html', {'form': record_form})

def lesson_record_edit(request, lesson_record_id=''):
    if request.method == 'POST':
        record_form = LessonRecordForm(request.POST)
        if record_form.is_valid():
            # Process record update
            modified_record_data = record_form.cleaned_data
            update_a_lesson_record(lesson_record_id, modified_record_data)
            return HttpResponseRedirect('/schooladmin/lesson_records/')
    else:
        modified_lesson_record = get_a_lesson_record(lesson_record_id)
        modified_lesson_record_data = {
            'user': modified_lesson_record.user.id,
            'genre': modified_lesson_record.genre.id,
            'attended_date': modified_lesson_record.attended_date,
            'school_hours': modified_lesson_record.school_hours,
        }
        record_form = LessonRecordForm(modified_lesson_record_data)

    context = {'form': record_form, 'lesson_record_id': lesson_record_id}
    return render(request, 'schooladmin/lesson_record_edit.html', context)

def invoices_list(request):
    if request.method == 'POST':
        month_form = GenericMonthPickerForm(request.POST)
        if month_form.is_valid():
            target_month = month_form.cleaned_data['target_month']
    else:
        month_form = GenericMonthPickerForm()
        today = date.today()
        target_month = date(today.year, today.month, 1)
    ## Get invoices for target month
    invoices = get_invoice_for_month(target_month)

    context = {'form': month_form, 'invoices': invoices}
    return render(request, 'schooladmin/invoices_list.html', context)


def reports(request):
    if request.method == 'POST':
        month_form = GenericMonthPickerForm(request.POST)
        if month_form.is_valid():
            target_month = month_form.cleaned_data['target_month']
    else:
        month_form = GenericMonthPickerForm()
        today = date.today()
        target_month = date(today.year, today.month, 1)
    ## Get a report by genre and sex
    report_by_genre_sex = get_sales_report_by_genre_sex_for_month(target_month)
    ## Get a report by genre, sex and age
    report_by_genre_sex_age = get_sales_report_by_genre_sex_age_for_month(target_month)

    context = {
        'form': month_form,
        'report_by_genre_sex': report_by_genre_sex,
        'report_by_genre_sex_age': report_by_genre_sex_age,
    }
    return render(request, 'schooladmin/reports.html', context)

