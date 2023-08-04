# DRF-Library-project


Project of "Library service API". For online borrowing books from library. Written on Django REST Framework, uses telegram notifications


## Installing

Use this commands for installation of this project on your localhost

```shell
git clone https://github.com/Roman28101/DRF-Library-project
cd DRF_library_project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
* create .env file in main directory
* set data into it (use .env.sample for reference)

```
python manage.py migrate
python manage.py runserver
```




## Get access to project

* Download [ModHeader](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en)
* create user - /api/user/register
* get access token /api/user/token/



## Features

* JSON Web Token authenticated
* Documentation /api/doc/swagger/
* Only Admin can add books
* Authenticated users can manage borrowings
* Filtering borrowings by user, and status
