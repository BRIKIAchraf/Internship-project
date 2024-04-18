# Wait for the internet connection to be available

while ! ping -c 1 -W 1 google.com; do
    sleep 1
done

# Install Python3 pip if not already installed
sudo apt-get update && sudo apt-get install -y python3-pip

# Navigate to the app directory and install requirements
cd /home/pi/app
sudo pip3 install -r requirements.txt

# Remove this script from /etc/rc.local
sudo sed -i '/install_requirements.sh/d' /etc/rc.local

# Reboot the system to finalize installation
sudo reboot
