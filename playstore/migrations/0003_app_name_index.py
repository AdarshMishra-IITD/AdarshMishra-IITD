# Generated manually for adding index & ordering
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('playstore', '0002_alter_app_reviews_count'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='app',
            options={'ordering': ['name']},
        ),
        migrations.AddIndex(
            model_name='app',
            index=models.Index(fields=['name'], name='app_name_idx'),
        ),
    ]
