# Generated by Django 3.0.5 on 2020-10-21 12:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerPreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_list_order', models.CharField(default='none', max_length=500)),
                ('length', models.IntegerField(default=0)),
                ('post_per_day', models.IntegerField(default=0)),
                ('instagram', models.BooleanField(default=False)),
                ('facebook', models.BooleanField(default=False)),
                ('completed', models.BooleanField(default=False)),
                ('manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ManagerEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluation_started', models.BooleanField(default=False)),
                ('accepted', models.BooleanField(default=False)),
                ('declined', models.BooleanField(default=False)),
                ('evaluation_completed', models.BooleanField(default=False)),
                ('answer_one_caption_one', models.TextField(default='none', max_length=2200)),
                ('answer_one_caption_two', models.TextField(default='none', max_length=2200)),
                ('answer_one_caption_three', models.TextField(default='none', max_length=2200)),
                ('answer_two_caption', models.TextField(default='none', max_length=2200)),
                ('answer_two_what_are_problems', models.TextField(default='none', max_length=2200)),
                ('answer_two_img', models.ImageField(default='default.jpg', upload_to='application_pics')),
                ('answer_three_caption', models.TextField(default='none', max_length=2200)),
                ('answer_three_img', models.ImageField(default='default.jpg', upload_to='application_pics')),
                ('choose_job', models.BooleanField(default=False)),
                ('manager', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
