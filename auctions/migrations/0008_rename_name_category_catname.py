# Generated by Django 4.2.6 on 2023-11-01 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0007_alter_listing_category_alter_listing_watchlistedby"),
    ]

    operations = [
        migrations.RenameField(
            model_name="category",
            old_name="name",
            new_name="catName",
        ),
    ]