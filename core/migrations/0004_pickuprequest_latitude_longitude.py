from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_contactmessage"),
    ]
    operations = [
        migrations.AddField(
            model_name="pickuprequest",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="pickuprequest",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
