from django.db import migrations, models

def load_auction_houses(apps, schema_editor):
    AuctionHouse = apps.get_model("watchapp", "AuctionHouse")
    
    antiquorum = AuctionHouse(id=1,name='Antiquorum',base_url='')
    antiquorum.save()

    artcurial = AuctionHouse(id=2,name='Artcurial',base_url='')
    artcurial.save()

    bonhams = AuctionHouse(id=3,name='Bonhams',base_url='')
    bonhams.save()

    bukowskis = AuctionHouse(id=4,name='Bukowskis',base_url='')
    bukowskis.save()

    christies = AuctionHouse(id=5,name='Christies',base_url='')
    christies.save()

    dorotheum = AuctionHouse(id=6,name='Dorotheum',base_url='')
    dorotheum.save()

    monacolegend = AuctionHouse(id=7,name='Heritage',base_url='')
    monacolegend.save()
    

    phillips = AuctionHouse(id=8,name='Phillips',base_url='')
    phillips.save()

    sothebys = AuctionHouse(id=9,name='Sothebys',base_url='')
    sothebys.save()

    monacolegend = AuctionHouse(id=10,name='Monacolegend',base_url='')
    monacolegend.save()

class Migration(migrations.Migration):
    dependencies = [
        ('watchapp', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(load_auction_houses)
    ]