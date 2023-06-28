import jenkins
import json
import os



host = "http://3.83.53.67:8080/"
username = "admin" #jenkins username here
password = "11b27fc3d18677c67bb6fe4183035cad70" # Jenkins user password / api token here
server = jenkins.Jenkins(host, username=username, password=password) #automation_user_password

user = server.get_whoami()
version = server.get_version()
print('Hello %s from Jenkins %s' % (user['fullName'], version))

config_xml = open("config.xml", mode='r', encoding='utf-8').read()
server.create_job("Seed_Jobs", config_xml)
