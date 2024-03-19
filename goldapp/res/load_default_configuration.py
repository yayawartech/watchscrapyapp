from django.db import migrations, models

def load_default_configuration(apps, schema_editor):
    Configuration = apps.get_model("goldapp", "Configuration")
    
    config = Configuration(id=1,gold_c=7.0,platinum_c=7.0,silver_c=7.0,gold_sp=99.9,platinum_sp=99.9,silver_sp=99.9,platinum_bp=99.9)
    config.save()

class Migration(migrations.Migration):
    dependencies = [
        ('goldapp', 'load_old_data'),
    ]
    operations = [
        migrations.RunPython(load_default_configuration)
    ]