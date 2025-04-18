# Generated by Django 5.0.2 on 2024-03-19 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watchapp', 'populate_auction_house'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='actual_lots',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='auction',
            name='job',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='job',
            name='process',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='lot',
            name='job',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lot',
            name='search_all',
            field=models.TextField(default=None),
        ),
        migrations.AlterField(
            model_name='auction',
            name='name',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='auction',
            name='place',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='auction',
            name='url',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='auctionhouse',
            name='base_url',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='auctionhouse',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='lot',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='lot',
            name='images',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='lot',
            name='title',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='lot',
            name='url',
            field=models.CharField(max_length=500),
        ),
    ]
