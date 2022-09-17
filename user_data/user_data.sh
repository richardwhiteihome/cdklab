#!/bin/bash
sudo yum update -y
sudo yum makecache
sudo adduser apache

sudo yum install -y amazon-linux-extras
sudo amazon-linux-extras enable php8.0
sudo yum clean metadata
sudo yum install  -y

sudo yum install php php-{pear,cgi,common,curl,mbstring,gd,mysqlnd,gettext,bcmath,json,xml,fpm,intl,zip,imap} -y
sudo yum install httpd-tools wget -y
sudo yum install php-pecl-zip php-cli php-pdo -y
sudo yum install httpd mod_ssl -y

sudo systemctl enable --now httpd

