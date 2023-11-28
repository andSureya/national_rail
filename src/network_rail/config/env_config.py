from os import environ

USERNAME = environ.get('EMAIL', None)
PASSWORD = environ.get('PASSWORD', None)

if not USERNAME:
    USERNAME = input("Enter your openFeed email address: ")

if not PASSWORD:
    PASSWORD = input("Enter your openFeed password: ")

