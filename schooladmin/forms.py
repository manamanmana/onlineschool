from django import forms
from .models import User, Genre
from datetime import date, timedelta

## UserForm Form
class UserForm(forms.Form):
    SEX_ON_USER = (
        ("f", "女性"),
        ("m", "男性"),
    )

    name = forms.CharField(
        label="名前",
        max_length=255,
        min_length=1,
        error_messages={
            'required': "名前の入力が必要です。",
            'max_length': "名前は1文字以上255文字以下です。",
            'min_length': "名前は1文字以上255文字以下です。",
        },
    )

    sex = forms.ChoiceField(
        choices=SEX_ON_USER,
        label="性別",
        error_messages={
            'required': '性別を選択してください',  
        },
    )

    age = forms.IntegerField(
        min_value=0,
        label="年齢",
        widget=forms.TextInput,
        error_messages={
            'required': '年齢は0歳以上の半角数字で入力してください。',
            'invalid': '年齢は0歳以上の半角数字で入力してください。',
            'min_value': '年齢は0歳以上の半角数字で入力してください。',
        },
    )

## LessonRecordForm Form
class LessonRecordForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label=None,
        label="顧客名",
    )

    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        empty_label=None,
        label="ジャンル",
    )

    attended_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        label="受講日",
        help_text="YYYY-MM-DD形式で入力ください。",
        error_messages={
            'required': '受講日は必須です。YYYY-MM-DD形式で入力してください。',
            'invalid': '受講日は必須です。YYYY-MM-DD形式で入力してください。',
        },
    )

    school_hours = forms.IntegerField(
        min_value=1,
        max_value=12,
        label="受講時間（h）",
        widget=forms.TextInput,
        error_messages={
            'required': '受講時間は必須です。1から12までの半角数字で入力してください。',
            'invalid': '受講時間は必須です。1から12までの半角数字で入力してください。',
            'max_value': '受講時間は必須です。1から12までの半角数字で入力してください。',
            'min_value': '受講時間は必須です。1から12までの半角数字で入力してください。',
        },
    )

## Utility function for GenericMonthPickerForm CHOICE
def make_four_month():
    today = date.today()
    one_month_delta = timedelta(days=30)

    this_month = date(today.year, today.month, 1)
    one_month_before = date(
            (this_month - one_month_delta).year, 
            (this_month - one_month_delta).month, 
            1)
    two_month_before = date(
            (one_month_before - one_month_delta).year, 
            (one_month_before - one_month_delta).month, 
            1)
    three_month_before = date(
            (two_month_before - one_month_delta).year, 
            (two_month_before - one_month_delta).month, 
            1)
    four_month_before = date(
            (three_month_before - one_month_delta).year, 
            (three_month_before - one_month_delta).month, 
            1) 

    this_month_val = '{0}-{1}-{2}'.format(
            this_month.year, 
            this_month.month, 
            this_month.day) 
    this_month_label = '{0}年{1}月'.format(
            this_month.year, 
            this_month.month)
    one_month_before_val = '{0}-{1}-{2}'.format(
            one_month_before.year,
            one_month_before.month,
            one_month_before.day)
    one_month_before_label = '{0}年{1}月'.format(
            one_month_before.year,
            one_month_before.month)
    two_month_before_val = '{0}-{1}-{2}'.format(
            two_month_before.year,
            two_month_before.month,
            two_month_before.day)
    two_month_before_label = '{0}年{1}月'.format(
            two_month_before.year,
            two_month_before.month)
    three_month_before_val = '{0}-{1}-{2}'.format(
            three_month_before.year,
            three_month_before.month,
            three_month_before.day)
    three_month_before_label = '{0}年{1}月'.format(
            three_month_before.year,
            three_month_before.month)
    four_month_before_val = '{0}-{1}-{2}'.format(
            four_month_before.year,
            four_month_before.month,
            four_month_before.day)
    four_month_before_label = '{0}年{1}月'.format(
            four_month_before.year,
            four_month_before.month)


    MONTH_CHOICE = (
        (this_month_val, this_month_label),
        (one_month_before_val, one_month_before_label),
        (two_month_before_val, two_month_before_label),
        (three_month_before_val, three_month_before_label),
        (four_month_before_val, four_month_before_label),
    )

    return MONTH_CHOICE

## GenericMonthPickerForm Form
class GenericMonthPickerForm(forms.Form):
    target_month = forms.DateField(
            input_formats=['%Y-%m-%d'],
            widget=forms.Select(choices=make_four_month()), 
            label='月選択',
            error_messages={
                'required':'対象月を選択してください。',
                'invalid': '対象月を選択してください。',
            },
    )


