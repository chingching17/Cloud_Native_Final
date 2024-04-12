# Cloud_Native_Final  
## 製作開發環境  
```
docker build -t cn_django_dev .
docker run -p 8012:8000 -it -v ${pwd}:/codeForDev/ cn_django_dev bash  # For windows
```  
## create django project
```
django-admin startproject mysite
cd mysite
ls
```  
可以看到多了 manage.py 跟 mysite  
## 將 server 跑起來  
將以下兩行跑完之後在網址那邊下 127.0.0.1:8012  
```
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```