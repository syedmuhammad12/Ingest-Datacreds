# Generated by Django 4.1.2 on 2023-12-21 10:44

from django.db import migrations, models
import django.db.models.deletion
import file_management.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('file_templates', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='DuplicateFilesTrack',
            fields=[
                ('duplicate_file_id', models.AutoField(primary_key=True, serialize=False)),
                ('download_type', models.CharField(blank=True, max_length=30, null=True)),
                ('file_id', models.CharField(blank=True, max_length=500, null=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'duplicate_files_track',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id_file', models.AutoField(primary_key=True, serialize=False)),
                ('file_name', models.FileField(blank=True, max_length=500, null=True, upload_to=file_management.models.get_upload_file_path)),
                ('original_file_name', models.CharField(max_length=500, null=True)),
                ('file_type', models.CharField(blank=True, max_length=500, null=True)),
                ('file_format', models.CharField(blank=True, max_length=500, null=True)),
                ('file_size', models.CharField(blank=True, max_length=50, null=True)),
                ('is_data_extracted', models.CharField(blank=True, default=0, max_length=1, null=True)),
                ('pdf_page_count', models.CharField(blank=True, default=1, max_length=3, null=True)),
                ('is_delete', models.CharField(choices=[(0, '0'), (1, '1')], default=0, max_length=25)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('updated_datetime', models.DateTimeField(auto_now=True)),
                ('file_template_id', models.ForeignKey(db_column='file_template_id', on_delete=django.db.models.deletion.DO_NOTHING, related_name='file_template', to='file_templates.filetemplatesmodel')),
            ],
            options={
                'db_table': 'file_management',
            },
        ),
    ]