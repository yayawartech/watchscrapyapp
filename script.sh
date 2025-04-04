#!/bin/bash

PROJECT_MAIN_DIR_NAME="watchscrapyapp"

echo "Starting..."
sudo apt update

# Assuming you have already cloned the project manually, you can skip the clone step.
# Make sure the project directory exists under /home/ubuntu
if [ ! -d "/home/ubuntu/$PROJECT_MAIN_DIR_NAME" ]; then
    echo "Error: Project directory /home/ubuntu/$PROJECT_MAIN_DIR_NAME does not exist. Please clone the repository first."
    exit 1
fi

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

# Setup Django application
echo "Migrate database"
python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" migrate --database=default

python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" migrate --database=awsrds
echo "Secondary database migration complete"

echo "Database migration completed"

echo "Collect staticfiles"
python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" collectstatic --noinput

# Give proper ownership and permissions for static files
sudo chown -R www-data:www-data /home/ubuntu/$PROJECT_MAIN_DIR_NAME/staticfiles
sudo chmod -R 755 /home/ubuntu/$PROJECT_MAIN_DIR_NAME/staticfiles

# Copy Gunicorn socket and service files with appropriate permissions
echo "Copying Gunicorn socket and service files..."
if [[ -f "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.socket" && -f "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.service" ]]; then
    sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.socket" "/etc/systemd/system/gunicorn.socket"
    sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/gunicorn/gunicorn.service" "/etc/systemd/system/gunicorn.service"
else
    echo "Gunicorn socket or service file not found."
    exit 1
fi

# Set permissions for Gunicorn service
sudo chown root:root /etc/systemd/system/gunicorn.socket
sudo chown root:root /etc/systemd/system/gunicorn.service
sudo chmod 644 /etc/systemd/system/gunicorn.socket
sudo chmod 644 /etc/systemd/system/gunicorn.service

# Start and enable Gunicorn service
sudo systemctl daemon-reload
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service

echo "Gunicorn setup completed"

# Install Nginx
echo "Setting up nginx"
sudo apt install -y nginx

# Remove the default site from Nginx
sudo rm /etc/nginx/sites-enabled/default

# Copy the Nginx configuration file and set proper permissions
sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/nginx/nginx.conf" "/etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME"
sudo chown root:root /etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME
sudo chmod 644 /etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME

# Create the necessary symbolic link in sites-enabled
sudo ln -s /etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME /etc/nginx/sites-enabled/

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# ====================================================================================

echo "Setting up Chromedriver..."
cd /home/ubuntu
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

# Restart Nginx and Gunicorn services to apply changes
sudo systemctl restart nginx gunicorn

echo "Congratulations, Deployment Completed!"
echo "Create superuser and your application is ready to access"
