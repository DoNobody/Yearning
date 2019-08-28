# Generated by Django 2.0.1 on 2018-11-07 06:41

import core.models
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('group', models.CharField(max_length=40)),
                ('department', models.CharField(max_length=40)),
                ('auth_group', models.TextField(null=True)),
                ('real_name', models.CharField(default='请添加真实姓名', max_length=100, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='applygrained',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=50)),
                ('work_id', models.CharField(max_length=50, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
                ('permissions', core.models.JSONField()),
                ('auth_group', models.CharField(max_length=50, null=True)),
                ('real_name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DatabaseList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connection_name', models.CharField(max_length=50)),
                ('computer_room', models.CharField(max_length=50)),
                ('ip', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=150)),
                ('port', models.IntegerField()),
                ('password', models.CharField(max_length=50)),
                ('before', models.TextField(null=True)),
                ('after', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='globalpermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorization', models.CharField(db_index=True, max_length=50, null=True)),
                ('inception', core.models.JSONField(null=True)),
                ('ldap', core.models.JSONField(null=True)),
                ('message', core.models.JSONField(null=True)),
                ('other', core.models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='grained',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, max_length=50)),
                ('permissions', core.models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='query_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_id', models.CharField(db_index=True, max_length=50, null=True)),
                ('username', models.CharField(max_length=100, null=True)),
                ('date', models.CharField(max_length=50)),
                ('instructions', models.TextField(null=True)),
                ('query_per', models.SmallIntegerField(default=0, null=True)),
                ('connection_name', models.CharField(max_length=50, null=True)),
                ('computer_room', models.CharField(max_length=50, null=True)),
                ('export', models.SmallIntegerField(default=0, null=True)),
                ('audit', models.CharField(max_length=100, null=True)),
                ('time', models.CharField(max_length=100, null=True)),
                ('real_name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='querypermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_id', models.CharField(db_index=True, max_length=50, null=True)),
                ('username', models.CharField(max_length=100, null=True)),
                ('statements', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SqlDictionary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BaseName', models.CharField(max_length=100)),
                ('TableName', models.CharField(max_length=100)),
                ('Field', models.CharField(max_length=100)),
                ('Type', models.CharField(max_length=100)),
                ('Extra', models.TextField()),
                ('TableComment', models.CharField(max_length=100)),
                ('Name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SqlOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_id', models.CharField(blank=True, max_length=50)),
                ('username', models.CharField(blank=True, max_length=50)),
                ('status', models.IntegerField(blank=True)),
                ('type', models.SmallIntegerField(blank=True)),
                ('backup', models.SmallIntegerField(blank=True)),
                ('bundle_id', models.IntegerField(db_index=True, null=True)),
                ('date', models.CharField(blank=True, max_length=100)),
                ('basename', models.CharField(blank=True, max_length=50)),
                ('sql', models.TextField(blank=True)),
                ('text', models.TextField(blank=True)),
                ('assigned', models.CharField(blank=True, max_length=50)),
                ('delay', models.IntegerField(default=0, null=True)),
                ('rejected', models.TextField(blank=True)),
                ('real_name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SqlRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=100)),
                ('sql', models.TextField(blank=True)),
                ('error', models.TextField(null=True)),
                ('workid', models.CharField(max_length=50, null=True)),
                ('affectrow', models.CharField(max_length=100, null=True)),
                ('sequence', models.CharField(max_length=50, null=True)),
                ('execute_time', models.CharField(max_length=150, null=True)),
                ('backup_dbname', models.CharField(max_length=100, null=True)),
                ('SQLSHA1', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Todolist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('content', models.CharField(max_length=200)),
            ],
        ),
    ]
