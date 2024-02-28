# Django Library E-commerce

You can use the library project I made according to your wishes.

## Description

The purpose of my project is that users, as tenants, can share their books for rent online, and visitors can buy books shared by tenants. 
<br>
Users can receive books shared by tenants for a period of time they choose. User can add books to wish list. They can add or 
remove books from their wish list. When the book they want to buy is not in stock, I made a queue system so that the user is informed when 
the book is in stock. When the book is in stock, a notification is automatically sent to the user's e-mail address. The user can cancel 
the queue at any time. After the user selects the book or books for the period he wants to buy, he can add them to the product list. 
The user can change the number of books added to the product list or remove them from the product list. Users cannot buy their books 
in the product list because I did not make a payment system because I did not put my project into use as an e-commerce site.
<br>
Tenants can share and manage their books from the dashboard. The tenant can see which user bought the book in which date range and statistics about the general books about the books they share.
<br>
I used Jinja template engine as template language in the project. I made the backend with Python's Django framework and used jquery in the frontend.

## Installation

```bash
git clone https://github.com/ibrahimmuradov/django_library_e_commerce.git .
pip install -r requirements.txt
django-admin startproject core . 
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```
