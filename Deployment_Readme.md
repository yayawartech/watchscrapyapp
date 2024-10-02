# Watch Deployment Docs
## Clone the project
### Go inside the project directory
```
cd watchscrapyapp
```

### Give executable permission to script.sh file
``` 
sudo chmod +x script.sh
```
> **Note:**  Create .env file in project root directory and update S3 credentials and database similar to .sampleEnv
## Update S3 credentials in .env
```
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
```
## Update database credentials in .env
```
RDS_DB_NAME = ""
RDS_USER = ""
RDS_PASSWORD = ""
RDS_HOST = ""
RDS_PORT = ""
```

### go inside WatchInfo (project) 
```
cd WatchInfo
```
### Update ALLOWED_HOSTS in settings.py file
> **Note:** Put server's IP or domain inside ALLOWED_HOSTS
```
ALLOWED_HOSTS = ["165.22.181.81"]
```
# Execute script1.sh file
```
./script.sh
```

> **NOTE:** Activate virtualenv if not activated
```
source /home/ubuntu/watchscrapyapp/venv/bin/activate
```
### Create superuser
```
python /home/ubuntu/watchscrapyapp/manage.py createsuperuser
```
