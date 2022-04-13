# Generated by Django 2.2.16 on 2022-01-18 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0010_title_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="text",
            field=models.TextField(default="test"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="review",
            name="score",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
