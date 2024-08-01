from django.db import models


class AuctionHouse(models.Model):

    name = models.CharField(max_length=200)
    base_url = models.CharField(max_length=500)

    class Meta:
        app_label = "watchapp"


class Job(models.Model):

    name = models.CharField(max_length=500)
    urls = models.TextField()
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    status = models.CharField(max_length=100)
    process = models.IntegerField(default=0)

    auction_house = models.ForeignKey(AuctionHouse, on_delete=models.CASCADE)


class Auction(models.Model):

    name = models.CharField(max_length=250)
    job = models.CharField(max_length=100)
    date = models.DateField(null=True)
    place = models.CharField(max_length=200)
    url = models.CharField(max_length=500)
    actual_lots = models.IntegerField(default=0)

    auction_house = models.ForeignKey(AuctionHouse, on_delete=models.CASCADE)


class Lot(models.Model):

    url = models.CharField(max_length=500)
    job = models.CharField(max_length=100)
    status = models.CharField(max_length=40)
    lot_number = models.IntegerField()
    title = models.CharField(max_length=500)
    description = models.TextField()
    estimate_min_price = models.CharField(max_length=10)
    estimate_max_price = models.CharField(max_length=10)
    lot_currency = models.CharField(max_length=10)
    sold = models.IntegerField()
    sold_price = models.CharField(max_length=10)

    sold_price_dollar = models.IntegerField()
    # images = models.TextField()
    images = models.JSONField(default=list)
    # s3_image = models.TextField()
    s3_images = models.JSONField(default=list)

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    search_all = models.TextField(default=None)

    # def get_images(self):
    #     if not self.s3_images:
    #         return []  # Return an empty list if s3_images is None or empty

    #     imgs = self.s3_images
    #     imgsList = []
    #     for img in imgs:
    #         # Ensure img is a string and handle it properly
    #         if isinstance(img, str):
    #             imgsList.append(img.strip('[').strip(']').replace("'", ""))
    #     return imgsList
    def get_images(self):
        if self.s3_images:
            imgs = self.s3_images
        elif self.images:
            imgs = self.images
        else:
            return []  # Return an empty list if both are None or empty
        print(f'\n--- imgs:: {imgs} --- \n')
        imgsList = []
        for img in imgs:
            # Ensure img is a string and handle it properly
            if isinstance(img, str):
                imgsList.append(img.strip('[').strip(']').replace("'", ""))
        return imgsList

    def __str__(self):
        images = self.get_images()
        if images:
            return images[0]  # Return the first image if the list is not empty
        return ''  # Return an empty string if the list is empty

    def save(self, *args, **kwargs):
        title_txt = ""
        if isinstance(self.title, list):
            title_txt = ""+" ".join(self.title)
        else:
            title_txt = self.title
        descr_text = ""
        self.description = self.description.encode('utf-8', errors='ignore').decode('utf-8')
        if isinstance(self.description, list):
            descr_text = ""+" ".join(self.description)
        else:
            descr_text = self.description
        if title_txt is not None:
            self.search_all = title_txt+descr_text
        super(Lot, self).save(*args, **kwargs)


class Setup(models.Model):
    chromedriver = models.CharField(max_length=300)


"""
INSERT into watchapp_auctionhouse (name,base_url) values ('Antiquorum','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Artcurial','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Bonhams','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Bonhams','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Christies','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Dorotheum','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Heritage','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Phillips','');
INSERT into watchapp_auctionhouse (name,base_url) values ('Sothebys','');
INSERT into watchapp_auctionhouse (name,base_url) values ('MonacoLegend','');
"""
