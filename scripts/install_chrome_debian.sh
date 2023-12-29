#!/bin/sh

apt update
apt install -y libayatana-appindicator1 fonts-liberation
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome*.deb
apt --fix-broken install -y
