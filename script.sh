#!bin/bash

PROJECT_MAIN_DIR_NAME="watchscrapyapp"

echo "Starting..."
sudo apt update

# Install Python3 pip
sudo apt install -y python3-pip

# Install Nginx
sudo apt install -y nginx

# Install Virtualenv
sudo apt install -y virtualenv
sudo apt install python3-virtualenv        

# Create virtual environment
echo "Creating virtual environment..."
virtualenv "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv"

# Activate virtual environment
echo "Activating virtual environment..."
source "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv/bin/activate"

# Install dependencies
echo "Installing Python dependencies..."
pip install -r "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/requirements.txt"

pip install gunicorn whitenoise

echo "Dependencies installed successfully."

# Deactivate virtual environment to install and setup server
deactivate        

# Copy gunicorn socket and service files
sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.socket" "/etc/systemd/system/gunicorn.socket"
sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.service" "/etc/systemd/system/gunicorn.service"

# Start and enable Gunicorn service
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service

sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/nginx/nginx.conf" "/etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME"

# remote default from sites-enable
sudo rm /etc/nginx/sites-enable/default

sudo ln -s /etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME /etc/nginx/sites-enabled/        

sudo systemctl restart nginx

sudo service gunicorn restart

sudo service nginx restart 