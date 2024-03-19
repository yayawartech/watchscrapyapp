from django.db import migrations, models

def load_coins_information(apps, schema_editor):
    Coin = apps.get_model("goldapp", "Coin")
    
    row1 = Coin(id=1, name="Libra", pure_gold="7.325087", factor=0.92)
    row1.save()

    row2 = Coin(id=2, name="Media Libra", pure_gold="3.662500", factor=2)
    row2.save()

    row3 = Coin(id=3, name="Mexicana $1", pure_gold="0.450000", factor=0.9)
    row3.save()

    row4 = Coin(id=4, name="Mexicana $2", pure_gold="1.500000", factor=0.9)
    row4.save()

    row5 = Coin(id=5, name="Mexicana $2,50", pure_gold="1.874970", factor=0.9)
    row5.save()

    row6 = Coin(id=6, name="Mexicana $5", pure_gold="3.749940", factor=0.9)
    row6.save()

    row7 = Coin(id=7, name="Mexicana $10", pure_gold="7.500000", factor=0.9)
    row7.save()

    row8 = Coin(id=8, name="Mexicana $20", pure_gold="15.000000", factor=0.9)
    row8.save()

    row9 = Coin(id=9, name="Mexicana $50", pure_gold="37.500000", factor=0.9)
    row9.save()

    row10 = Coin(id=10, name="USA $1 ", pure_gold="1.504800", factor=0.9)
    row10.save()

    row11 = Coin(id=11, name="USA $2,5", pure_gold="3.761640", factor=0.9)
    row11.save()

    row12 = Coin(id=12, name="USA $5", pure_gold="7.523100", factor=0.9)
    row12.save()

    row13 = Coin(id=13, name="USA $10", pure_gold="15.046600", factor=0.9)
    row13.save()

    row14 = Coin(id=14, name="USA $20", pure_gold="30.093300", factor=0.9)
    row14.save()

    row15 = Coin(id=15, name="Aleman 5 marcos", pure_gold="1.791900", factor=0.9)
    row15.save()

    row16 = Coin(id=16, name="Aleman 10 marcos", pure_gold="3.584250", factor=0.9)
    row16.save()

    row17 = Coin(id=17, name="Aleman 20 marcos", pure_gold="7.168500", factor=0.9)
    row17.save()

    row18 = Coin(id=18, name="Austria 1 ducado", pure_gold="3.451000", factor=0.9)
    row18.save()

    row19 = Coin(id=19, name="Austria 4 ducado", pure_gold="13.804000", factor=0.9)
    row19.save()

    row20 = Coin(id=20, name="Austria 10 ducado", pure_gold="34.510000", factor=0.9)
    row20.save()

    row21 = Coin(id=21, name="Chile 50 pesos", pure_gold="9.152865", factor=0.9)
    row21.save()

    row22 = Coin(id=22, name="Chile 100 pesos", pure_gold="18.305730", factor=0.9)
    row22.save()

    row23 = Coin(id=23, name="Espana 10 pesetas", pure_gold="2.903220", factor=0.9)
    row23.save()

    row24 = Coin(id=24, name="Espana 20 pesetas", pure_gold="5.800000", factor=0.9)
    row24.save()

    row25 = Coin(id=25, name="Espana 25 pesetas", pure_gold="7.258050", factor=0.9)
    row25.save()

    row26 = Coin(id=26, name="Libra", pure_gold="13.325433", factor=0.92)
    row26.save()

    row27 = Coin(id=27, name="Media Libra", pure_gold="13.599016", factor=2)
    row27.save()

    row28 = Coin(id=28, name="Mexicana $3", pure_gold="13.872598", factor=0.9)
    row28.save()

    row29 = Coin(id=29, name="Mexicana $4", pure_gold="14.146181", factor=0.9)
    row29.save()

    row30 = Coin(id=30, name="Mexicana $2,51", pure_gold="14.419764", factor=0.9)
    row30.save()

    row31 = Coin(id=31, name="Mexicana $5", pure_gold="14.693346", factor=0.9)
    row31.save()

    row32 = Coin(id=32, name="Mexicana $10", pure_gold="14.966929", factor=0.9)
    row32.save()

    row33 = Coin(id=33, name="Mexicana $20", pure_gold="15.240512", factor=0.9)
    row33.save()

    row34 = Coin(id=34, name="Mexicana $50", pure_gold="15.514094", factor=0.9)
    row34.save()

    row35 = Coin(id=35, name="USA $2", pure_gold="15.787677", factor=0.9)
    row35.save()

    row36 = Coin(id=36, name="USA $2,6", pure_gold="16.061260", factor=0.9)
    row36.save()

    row37 = Coin(id=37, name="USA $5", pure_gold="16.334842", factor=0.9)
    row37.save()

    row38 = Coin(id=38, name="USA $10", pure_gold="16.608425", factor=0.9)
    row38.save()

class Migration(migrations.Migration):
    dependencies = [
        ('goldapp', 'load_carat_information'),
    ]
    operations = [
        migrations.RunPython(load_coins_information)
    ]