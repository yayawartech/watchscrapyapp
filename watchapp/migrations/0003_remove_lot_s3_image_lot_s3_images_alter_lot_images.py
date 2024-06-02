# Generated by Django 5.0.4 on 2024-05-26 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchapp', '0002_lot_s3_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lot',
            name='s3_image',
        ),
        migrations.AddField(
            model_name='lot',
            name='s3_images',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='lot',
            name='images',
            field=models.JSONField(default=list),
        ),
    ]
