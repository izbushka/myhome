# Initial raspberry setup:
* Set Wifi, Timezone in `sudo raspi-config`
* enable ssh: `sudo systemctl enable ssh`
sudo systemctl enable systemd-timesyncd.service
sudo systemctl start systemd-timesyncd.service
# Update system
* sudo apt update
* sudo apt upgrade

# Disable Swap
* sudo dphys-swapfile swapoff
* sudo systemctl disable dphys-swapfile

# Prepare scripts
* apt install git python3-venv
* cd /home
* mkdir scripts
* chown pi:pi scripts
* chmod 775 scripts
* mkdir db
* chown pi:pi db
* chmod 775 db
* cd scripts

# Install scripts
git clone backup.local:/home/scripts .

# Fstab: change according to example in system/etc/fstab
> TODO: try var/tmp in tmpfs
> read  superuser.com/a/168126/105936 IT IS NOT a good idea
> tmpfs /var/tmp tmpfs
> commit=N option: N secconds to commit, default 5, try more: 1800
> log to ram https://raspberrypi.stackexchange.com/questions/62533/how-can-i-reduce-the-writing-to-log-files/62536#62536
> cat /sys/fs/ext4/mmcblk0p2/lifetime_write_kbytes
> dumpe2fs /dev/mmcblk0p2|grep 'Lifetime writes'
> 4GB флешка погибает гдето на 300Гб пишут

# Raspberry Pi software
* sudo apt install git vim mc screen
* sudo apt install python3-venv
* sudo apt install sqlite3
* sudo apt install ntpdate tcpdump telnet
* sudo apt install msmtp msmtp-mta bsd-mailx
* sudo apt install mosquitto mosquitto-clients
* sudo apt install mpg123 ffmpeg festival
> For miio (xiaomi devices)
* sudo apt install python3-dev libffi-dev
> google assistant
* sudo apt install python3-dev portaudio19-dev libffi-dev libssl-dev
> nginx
* sudo apt install nginx-full
* sudo apt install libdbi-perl libjson-perl liburi-perl libtry-tiny-perl libdbd-sqlite3-perl
* sudo apt install nginx-extras

> FYI: Working with apt-file (search not installed libraries if python needs)
> apt util to find package by file (sudo apt-file update) *
> apt install apt-file
> apt-file update
> apt-file search libharfbuzz.so.0
> libharfbuzz0b: /usr/lib/arm-linux-gnueabihf/libharfbuzz.so.0
> apt install libharfbuzz


# pip modules
> Ensure 300Mb in /tmp! (if it is on tmpfs)
* python3 -m venv /home/scripts/venv/python3
* source venv/python3/bin/activate
* pip intall -r venv/requirements.txt

# install configs
* cat system/etc/nginx/nginx.conf > /etc/nginx/nginx.conf
* ln -s /home/scripts/nginx/nginx-api.cfg /etc/nginx/sites-enabled/nginx-api.cfg
* rm /etc/nginx/sites-enabled/default

* cat system/etc/mosquitto/mosquitto.conf > /etc/mosquitto/mosquitto.conf 

* cat system/etc/rsyncd.conf > /etc/rsyncd.conf
* cat system/etc/rsync.pass > /etc/rsync.pass

* cat system/etc/msmtprc > /etc/msmtprc

* cp daemons/*service /etc/systemd/system/
* chmod 644 /etc/systemd/system/*-monitor.service
* chmod 644 /etc/systemd/system/telegram-bot.service
* systemctl enable arduino-monitor.service
* systemctl enable cmd-monitor.service
* systemctl enable fcm-monitor.service
* systemctl enable gpio-monitor.service
* systemctl enable miio-monitor.service
* systemctl enable mqtt-monitor.service
* systemctl enable ping-monitor.service
* systemctl enable states-monitor.service
* systemctl enable zwave-monitor.service
* systemctl enable telegram-bot.service

* cat /home/scripts/system/var/spool/cron/crontabs/root |crontab -

* systemctl enable nginx
* systemctl enable mosquitto

# Z-wave: system states in /home/scripts/zwave/home is NOT in git!

# create sqlite databases

# setup watchdog (by systemd)
* cat system/etc/rsyncd.conf > /etc/systemd/system.conf
# setup syslog
* cat system/etc/rsyslog.conf > etc/rsyslog.conf
