from django.db import migrations, models

def load_carat_information(apps, schema_editor):
    CaratInformation = apps.get_model("goldapp", "CaratInformation")
    
    gold1 = CaratInformation(id=1,key_type="gold",key="22k",value=0.90)
    gold1.save()

    gold2 = CaratInformation(id=2,key_type="gold",key="18k",value=0.71)
    gold2.save()

    gold3 = CaratInformation(id=3,key_type="gold",key="14k",value=0.54)
    gold3.save()

    gold4 = CaratInformation(id=4,key_type="gold",key="9k",value=0.36)
    gold4.save()

    silver1 = CaratInformation(id=5,key_type="silver",key="925",value=0.93)
    silver1.save()

    silver2 = CaratInformation(id=6,key_type="silver",key="900",value=0.90)
    silver2.save()

    silver3 = CaratInformation(id=7,key_type="silver",key="800",value=0.80)
    silver3.save()

    silver4 = CaratInformation(id=8,key_type="silver",key="700",value=0.70)
    silver4.save()

class Migration(migrations.Migration):
    dependencies = [
        ('goldapp', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_carat_information)
    ]