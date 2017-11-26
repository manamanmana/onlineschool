from django.db import models

# Create your models here.

# User Model
class User(models.Model):
    name = models.CharField("名前", max_length=255)
    sex = models.CharField("性別", max_length=1)
    age = models.SmallIntegerField("年齢")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Genre Model
class Genre(models.Model):
    name = models.CharField("ジャンル", max_length=255) ## 英語、ファイナンス等
    basic_rate = models.IntegerField("基本料金", default=0) 
    min_basic_rate_apply_amount = models.SmallIntegerField("基本料金適用最低時間", default=0)
    max_basic_rate_apply_amount = models.SmallIntegerField("基本料金適用最高時間", default=744) ## 744 = 24h * 31days
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# MaterRate Model 従量料金
class MaterRate(models.Model):
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, db_index=True, verbose_name="ジャンル")
    amount_by_hour = models.IntegerField("従量料金", default=0) 
    min_mater_rate_apply_amount = models.SmallIntegerField("従量料金適用最低時間", default=0)
    max_mater_rate_apply_amount = models.SmallIntegerField("従量料金適用最高時間", default=744) ## 744 = 24h * 31days
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

# LessonRecord Model レッスン受講記録
class LessonRecord(models.Model):
    user = models.ForeignKey("User", on_delete=models.PROTECT, verbose_name="顧客名")
    genre = models.ForeignKey("Genre", on_delete=models.PROTECT, verbose_name="ジャンル")
    attended_date = models.DateField("受講日", db_index=True)
    school_hours = models.SmallIntegerField("受講時間（h）")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


