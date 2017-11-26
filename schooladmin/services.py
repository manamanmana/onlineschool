from .models import User, LessonRecord, MaterRate, Genre
import datetime

## User model related operations
def get_all_users():
    return User.objects.all()

def add_a_user(new_user_data):
    new_user = User(
        name = new_user_data['name'],
        sex = new_user_data['sex'],
        age = new_user_data['age'],
    )
    return new_user.save()

def get_a_user(user_id):
    return User.objects.get(pk=user_id)

def update_a_user(user_id, modified_user_data):
    modified_user = User.objects.get(pk=user_id)
    modified_user.name = modified_user_data['name']
    modified_user.sex = modified_user_data['sex']
    modified_user.age = modified_user_data['age']
    return modified_user.save()

## LessonRecord relatred operartions
def get_all_lesson_records():
     lesson_records = LessonRecord.objects.all().order_by('attended_date')
     result = []
     for record in lesson_records:
        row = {
            'id': record.id,
            'user': record.user.name,
            'genre': record.genre.name,
            'attended_date': record.attended_date,
            'school_hours': record.school_hours,
            'payment': calc_mater_charge_of_the_date(
                        record.user.id, 
                        record.genre.id, 
                        record.attended_date, 
                        record.school_hours),
        }
        result.append(row)
     return result


def add_a_lesson_record(new_lesson_record_data):
    new_lesson_record = LessonRecord(
        user = new_lesson_record_data['user'],
        genre = new_lesson_record_data['genre'],
        attended_date = new_lesson_record_data['attended_date'],
        school_hours = new_lesson_record_data['school_hours'],
    )
    return new_lesson_record.save()

def get_a_lesson_record(lesson_record_id):
    return LessonRecord.objects.get(pk=lesson_record_id)

def update_a_lesson_record(lesson_record_id, modified_lesson_record_data):
    modified_lesson_record = LessonRecord.objects.get(pk=lesson_record_id)
    modified_lesson_record.user = modified_lesson_record_data['user']
    modified_lesson_record.genre = modified_lesson_record_data['genre']
    modified_lesson_record.attended_date = modified_lesson_record_data['attended_date']
    modified_lesson_record.school_hours = modified_lesson_record_data['school_hours']
    return modified_lesson_record.save()

## Calculate Mater Chage for specified user, genre at the date
def calc_mater_charge_of_the_date(user_id, genre_id, attended_date, school_hours):
    ## Get all the LessonRecord of the user and genre and month 
    ## before the current attended_date
    first_date_of_the_month = datetime.date(attended_date.year, 
                                            attended_date.month, 1)
    lesson_records_by_prev = LessonRecord.objects.filter(
            user__id=user_id, 
            genre__id=genre_id, 
            attended_date__lt=attended_date, 
            attended_date__gte=first_date_of_the_month).order_by('attended_date')
    
    ## Get accumulated school_hours and payments by previous
    accum_school_hours_by_prev = 0
    
    for record in lesson_records_by_prev:
        accum_school_hours_by_prev = accum_school_hours_by_prev + record.school_hours
    accum_payments_by_prev = _calc_mater_charge(accum_school_hours_by_prev, genre_id)

    ## Calculate the accumulated payments by current
    accum_school_hours_by_current = accum_school_hours_by_prev + school_hours
    accum_payments_by_current = _calc_mater_charge(accum_school_hours_by_current, genre_id)

    ## Charge of the day
    charge_of_the_day = accum_payments_by_current - accum_payments_by_prev

    return charge_of_the_day

## Calculate mater charge logic
def _calc_mater_charge(accum_school_hours, genre_id):
    accum_payments = 0;

    mater_rates = MaterRate.objects.filter(
            genre__id=genre_id).order_by('min_mater_rate_apply_amount')
    for rate in mater_rates:
        if accum_school_hours > rate.min_mater_rate_apply_amount and accum_school_hours <= rate.max_mater_rate_apply_amount:
            accum_payments = accum_payments + (accum_school_hours - rate.min_mater_rate_apply_amount) * rate.amount_by_hour
        elif accum_school_hours > rate.max_mater_rate_apply_amount:
            accum_payments = accum_payments + (rate.max_mater_rate_apply_amount - rate.min_mater_rate_apply_amount) * rate.amount_by_hour
        else:
            pass

    return accum_payments


## Create Invoices structure for the specified month by each user
def get_invoice_for_month(month):
    # get range max month
    delta = datetime.timedelta(days=31)
    next_month = datetime.date((month + delta).year, (month + delta).month, 1)
    # get all the users at first
    users = User.objects.all()
    # Aggregate invoice by each user
    result = [_create_invoice_row(user, month, next_month) for user in users]

    return result

## Logic to create invoice row
def _create_invoice_row(user, month, next_month):
    # Query lesson_records for the user and the month
    lesson_records = LessonRecord.objects.filter(
            user__id=user.id, 
            attended_date__gte=month, 
            attended_date__lt=next_month).order_by('genre')
    
    # それぞれのInvoice行の計算
    calculated_row = _calc_invoice_row_value(user, lesson_records)
   
    # 表示用のジャンル・ラベルの生成
    genre_label = _create_genre_row(calculated_row['genre_set'])
    
    # 表示用一行の生成
    row = {
        'user_id': calculated_row['user_id'],
        'user_name': calculated_row['user_name'],
        'genre': genre_label,
        'lesson_count': calculated_row['lesson_count'],
        'invoice': calculated_row['invoice'],
    }

    return row

## Logic to calculate each invoice row value
def _calc_invoice_row_value(user, lesson_records):
    user_id = user.id     # 顧客ID
    user_name = user.name # 顧客名
    genre_set = set()     # ジャンル表示用
    lesson_count = 0      # 合計レッスン数
    invoice = 0           # 請求金額
    total_school_hours = dict()  # 請求金額に基本料金追加の為 ジャンル毎受講時間
    
    for record in lesson_records:
        genre_set.add(record.genre.name) # Uniq genre name
        lesson_count = lesson_count + 1  # Accumulate lesson count
        # Only mater charge
        invoice = invoice + calc_mater_charge_of_the_date(
                                user_id, 
                                record.genre.id, 
                                record.attended_date, 
                                record.school_hours)
        # ジャンルIDのキー毎に受講時間を追加していき、ジャンル毎受講時間算出
        total_school_hours[record.genre.id] = total_school_hours.get(record.genre_id, 0) + record.school_hours

    # 基本料金の追加ロジック
    for genre_id in total_school_hours.keys():
        # そのジャンルのトータル受講時間
        genre_total_hours = total_school_hours[genre_id]
        genre = Genre.objects.get(pk=genre_id)
        # そのジャンルの受講時間が適用範囲内であれば、invoiceに基本料金追加
        if genre_total_hours >= genre.min_basic_rate_apply_amount and genre_total_hours <= genre.max_basic_rate_apply_amount:
            invoice = invoice + genre.basic_rate

    return {
        'user_id': user_id,
        'user_name': user_name,
        'genre_set': genre_set,
        'lesson_count': lesson_count,
        'invoice': invoice,
    }

## Create genre label for invoice row
def _create_genre_row(genre_set):
    if len(genre_set) > 0:
        genre_label = '/'.join(genre_set) + '({0})'.format(len(genre_set))
    else:
        genre_label = ''

    return genre_label
   
## Create a sales report by genre and sex at the month
def get_sales_report_by_genre_sex_for_month(month):
    SEX_LIST = (
        ('f', '女'),
        ('m', '男'),
    )
    # get range max month
    delta = datetime.timedelta(days=31)
    next_month = datetime.date((month + delta).year, (month + delta).month, 1)
    # get all the genres
    genres = Genre.objects.all()
    # Aggregate the report by each genre
    results = []
    for genre in genres:
        for sex in SEX_LIST:
            row = _report_by_genre_sex_row(genre, sex, month, next_month)
            results.append(row)

    return results

## Logic to create report row by genre and sex
def _report_by_genre_sex_row(genre, sex, month, next_month):
    # Query lesson records by genre, sex and month range
    lesson_records = LessonRecord.objects.filter(
            genre__id=genre.id,
            user__sex=sex[0],
            attended_date__gte=month,
            attended_date__lt=next_month)
    # Calculate each report row
    calculated_row = _calc_report_row_by_genre_sex(genre, sex, lesson_records)
    return calculated_row

## Logic to calculate each report row value by genre and sex
def _calc_report_row_by_genre_sex(genre, sex, lesson_records):
    lesson_count = 0     # レッスン数
    user_id_set = set()  # 受講者数算出のためのユニークなユーザIDセット
    sales = 0            # 売上累積用
    total_school_hours = dict() # 請求金額に基本料金追加の為 ジャンル＋ユーザ毎受講時間

    for record in lesson_records:
        lesson_count = lesson_count + 1 # Accumulate lesson count
        user_id_set.add(record.user.id) # Uniq user_id
        # Only mater charge
        sales = sales + calc_mater_charge_of_the_date(
                            record.user.id, 
                            genre.id, 
                            record.attended_date, 
                            record.school_hours)
        # ユーザIDのキー毎に受講時間を追加していき受講時間算出（ ジャンルは単一）
        total_school_hours[record.user.id] = total_school_hours.get(record.user.id, 0) + record.school_hours

    # 基本料金の追加ロジック
    for user_id in total_school_hours.keys():
        # そのユーザのジャンルにおけるトータル受講時間
        total_hours = total_school_hours[user_id]
        # そのユーザの受講時間が適用範囲であればsalesに基本料金追加
        if total_hours >= genre.min_basic_rate_apply_amount and total_hours <= genre.max_basic_rate_apply_amount:
            sales = sales + genre.basic_rate

    return {
        'genre': genre.name,
        'sex': sex[1],
        'lesson_count': lesson_count,
        'user_count': len(user_id_set),
        'sales': sales,
    }
    
## Create a sales report by genre, sex and age at the month
def get_sales_report_by_genre_sex_age_for_month(month):
    SEX_LIST = (
        ('f', '女'),
        ('m', '男'),
    )

    AGE_LIST = (
        ('10', '19', '10代'),
        ('20', '29', '20代'),
        ('30', '39', '30代'),
        ('40', '49', '40代'),
        ('50', '59', '50代'),
        ('60', '69', '60代'),
        ('70', '79', '70代'),
    )
    # get range max month
    delta = datetime.timedelta(days=31)
    next_month = datetime.date((month + delta).year, (month + delta).month, 1)
    # get all the genres
    genres = Genre.objects.all()
    # Aggregate the report by each genre
    results = []
    for genre in genres:
        for sex in SEX_LIST:
            for age in AGE_LIST:
                row = _report_by_genre_sex_age_row(genre, sex, age, month, next_month)
                results.append(row)

    return results

## Logic to create report row by genre, sex and age
def _report_by_genre_sex_age_row(genre, sex, age, month, next_month):
    # Query lesson records by genre, sex, age and month range
    lesson_records = LessonRecord.objects.filter(
            genre__id=genre.id,
            user__sex=sex[0],
            user__age__gte=age[0],
            user__age__lte=age[1],
            attended_date__gte=month,
            attended_date__lt=next_month)
    # Calculate each report row
    calculated_row = _calc_report_row_by_genre_sex_age(genre, sex, age, lesson_records)
    return calculated_row

## Logic to calculate each report row value by genre, sex and age
def _calc_report_row_by_genre_sex_age(genre, sex, age, lesson_records):
    lesson_count = 0    # レッスン数
    user_id_set = set() # 受講者数算出のためのユニークなユーザIDセット
    sales = 0           # 売上累積用
    total_school_hours = dict() # 請求金額に基本料金追加の為 ジャンル＋ユーザ毎受講時間

    for record in lesson_records:
        lesson_count = lesson_count + 1 # Accumulate lesson count
        user_id_set.add(record.user.id) # Uniq user_id
        # Only mater charge
        sales = sales + calc_mater_charge_of_the_date(
                            record.user.id,
                            genre.id,
                            record.attended_date,
                            record.school_hours)
        # ユーザIDのキー毎に受講時間を追加していき受講時間算出（ ジャンルは単一）
        total_school_hours[record.user.id] = total_school_hours.get(record.user.id, 0) + record.school_hours

    # 基本料金の追加ロジック
    for user_id in total_school_hours.keys():
        # そのユーザのジャンルにおけるトータル受講時間
        total_hours = total_school_hours[user_id]
        # そのユーザの受講時間が適用範囲であればsalesに基本料金追加
        if total_hours >= genre.min_basic_rate_apply_amount and total_hours <= genre.max_basic_rate_apply_amount:
            sales = sales + genre.basic_rate

    return {
        'genre': genre.name,
        'sex': sex[1],
        'age': age[2],
        'lesson_count': lesson_count,
        'user_count': len(user_id_set),
        'sales': sales,
    }

