# Django Project with Scrapy Integration

This Django project integrates the Scrapy web crawling and scraping framework.

## Installation

1. Clone the repository:
``` 
https://github.com/yayawartech/watchscrapyapp.git
```

2. Navigate to the project directory:
``cd watchscrapyapp``

3. Install Python dependencies:
```
pip install -r requirements.txt
```

4. Run Django migrations:
### While migrating, first of all migrate default database and then migrate awsrds database 
```
python manage.py migrate --database=default && python manage.py migrate --database=awsrds 
```
5. Create superuser
``python manage.py createsuperuser ``

6. Update S3 credentials in WatchInfo/settings.py
```
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
```

7. Give the path to scrapy spider in: watchapp/utils/scrapper.py(optional)

8. Run development server
```
python manage.py runserver
```

---
# For running scrapy only

1. navigate to the folder watchscrapy
``` 
cd watchscrapy
```

2. Syntax for running:
scrapy crawl <spiderName>

``scrapy crawl antiquorumSpider``
``scrapy crawl artcurialSpider``
``scrapy crawl bonhamsSpider``
``scrapy crawl bukowskisSpider``
``scrapy crawl christiesSpider``
``scrapy crawl dorotheumSpider``
``scrapy crawl heritageSpider``
``scrapy crawl phillipsSpider``
``scrapy crawl sothebysSpider``
