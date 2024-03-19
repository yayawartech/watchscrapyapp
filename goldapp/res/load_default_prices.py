from django.db import migrations, models
from datetime import datetime

def load_default_prices(apps, schema_editor):
    GoldPriceWeight = apps.get_model("goldapp", "GoldPriceWeight")
    
    gold_price = 44.00
    gold_weight = 1706.00
    platinum_weight = 894.00
    silver_weight = 15.00
    last_updated = datetime.now()

    goldPrice = GoldPriceWeight(id=1,gold_price=gold_price,gold_weight=gold_weight,platinum_weight=platinum_weight,silver_weight=silver_weight,last_updated=last_updated)
    goldPrice.save()

class Migration(migrations.Migration):
    dependencies = [
        ('goldapp', 'load_default_configuration'),
    ]
    operations = [
        migrations.RunPython(load_default_prices)
    ]