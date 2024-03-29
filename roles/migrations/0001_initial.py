# Generated by Django 4.1.2 on 2023-12-21 10:43

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Modules',
            fields=[
                ('IdModuleAccess', models.AutoField(db_column='idmodule_access', primary_key=True, serialize=False)),
                ('ModuleName', models.CharField(db_column='module_name', max_length=45)),
            ],
            options={
                'db_table': 'modules',
            },
        ),
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(max_length=90, unique=True)),
                ('role_description', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2023, 12, 21, 16, 13, 32, 197968), null=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime(2023, 12, 21, 16, 13, 32, 198964), null=True)),
            ],
            options={
                'db_table': 'Roles',
            },
        ),
        migrations.CreateModel(
            name='RoleHasModules',
            fields=[
                ('IdRoleHasModuleAccess', models.AutoField(db_column='idrole_has_module_access', primary_key=True, serialize=False)),
                ('IdModuleAccess', models.ForeignKey(blank=True, db_column='idmodule_access', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='roles.modules')),
                ('IdRole', models.ForeignKey(blank=True, db_column='id_role', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='roles.roles')),
            ],
            options={
                'db_table': 'role_has_modules',
            },
        ),
    ]
