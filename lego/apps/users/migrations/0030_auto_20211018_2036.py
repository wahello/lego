# Generated by Django 3.0.14 on 2021-10-18 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0029_auto_20210921_1835"),
    ]

    operations = [
        migrations.AlterField(
            model_name="abakusgroup",
            name="level",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="abakusgroup",
            name="lft",
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name="abakusgroup",
            name="rght",
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
