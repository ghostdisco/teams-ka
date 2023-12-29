#!/bin/sh

apt-get update
apt-get install -y libappindicator1 fonts-liberation
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get update
dpkg -i google-chrome*.deb

