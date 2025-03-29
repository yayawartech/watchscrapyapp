#!/bin/bash

PROJECT_MAIN_DIR_NAME="watchscrapyapp"

echo "Starting..."
sudo apt update

# Create a directory and copy the project to /home/ubuntu
mkdir -p /home/ubuntu

sudo ln -s /root/$PROJECT_MAIN_DIR_NAME /home/ubuntu/$PROJECT_MAIN_DIR_NAME
echo "Project linked to the path /home/ubuntu/$PROJECT_MAIN_DIR_NAME"

# Create virtual environment
echo "Creating virtual environment..."
sudo apt install -y virtualenv
virtualenv "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv"

# Activate virtual environment
echo "Activating virtual environment..."
source "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv/bin/activate"

# Install dependencies
echo "Installing Python dependencies..."
pip install -r "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/requirements.txt"
echo "Dependencies installed successfully."

# Setup django application
echo "Migrate database"
python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" migrate --database=default

python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" migrate --database=awsrds
echo "Secondary database migration complete"

echo "Database migration completed"
 
echo "Collect staticfiles"
python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" collectstatic --noinput

sudo chown -R www-data:www-data /home/ubuntu/$PROJECT_MAIN_DIR_NAME/staticfiles
sudo chmod 755 /root/$PROJECT_MAIN_DIR_NAME/staticfiles

# Copy gunicorn socket and service files
echo "Copying gunicorn socket and service files..."
sudo chown -R www-data:www-data /home/ubuntu/$PROJECT_MAIN_DIR_NAME

if [[ -f "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.socket" && -f "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.service" ]]; then
    sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.socket" "/etc/systemd/system/gunicorn.socket"
    sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.service" "/etc/systemd/system/gunicorn.service"
else
    echo "Gunicorn socket or service file not found."
    exit 1
fi

# Start and enable Gunicorn service
sudo systemctl daemon-reload
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service

echo "Gunicorn setup completed"

# Install Nginx
echo "Setting up nginx"
sudo apt install -y nginx

# remote default from sites-enable
sudo rm /etc/nginx/sites-enabled/default

sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/nginx/nginx.conf" "/etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME"

sudo ln -s /etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME /etc/nginx/sites-enabled/        

sudo nginx -t
sudo nginx -s reload


# ====================================================================================

echo "Setting up chromedriver..."
cd 
echo "Downloading google-chrome"
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

echo "Install Google Chrome"
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
echo "Google-chrome installation completed"
google-chrome --version

echo "Installing chromedriver"
wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.89/linux64/chromedriver-linux64.zip

sudo apt install -y unzip
sudo apt-get install -y libxss1 libappindicator3-1 libindicator7

unzip chromedriver-linux64.zip

sudo mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

echo "Chromedriver setup completed"
chromedriver --version

sudo systemctl restart nginx gunicorn

echo "Congratulations, Deployment Completed!"
echo "Create superuser and your application is ready to access"