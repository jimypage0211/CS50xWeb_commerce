# Generated by Django 4.2.6 on 2023-10-28 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0003_remove_listing_watchlistedby_delete_category_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name="listing",
            name="categories",
            field=models.ManyToManyField(
                blank=True, related_name="listings", to="auctions.category"
            ),
        ),
    ]