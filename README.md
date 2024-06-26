# Cloud_Native_Final  
## 製作開發環境  
```
docker build -t cn_django_dev .
docker run -p 8012:8000 -it -v ${pwd}:/codeForDev/ cn_django_dev bash  # For windows
```  
## 之後要進去  
這是我的，避免每次都開新的 container  
```
docker exec -it cool_bartik bash
```
## create django project
這步我做好了，其他人如果是直接 clone 下來可以跳過這一步  
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
python manage.py runserver 0.0.0.0:8000 &
```  
## Create Superuser  
user name 設定為 admin  
密碼設定為 zzbc1234
```
python manage.py createsuperuser
```
## 建立 web app  
這步我做好了，其他人如果是直接 clone 下來可以跳過這一步  
* 接著我會到 /mysite/settings.py 修改增加 INSTALLED_APPS
```
python manage.py startapp web_cn
```
## Add urls.py  
* 在 /web_cn 下新增 urls.py
* 修改 mysite/urls.py
* 修改 web_cn/urls.py
* 在 /web_cn 下新增 templates/*，之後...  
[參考這部](https://www.youtube.com/watch?v=ey8EXTjRuag&list=PLCC34OHNcOtqW9BJmgQPPzUpJ8hl49AGy&index=46&ab_channel=Codemy.com&t=8m)  
## Add CSS file  
* 在 /web_cn 下新增 static/ 
* 每次新增 static 都需要重跑 runserver   
[參考這部](https://www.youtube.com/watch?v=ey8EXTjRuag&list=PLCC34OHNcOtqW9BJmgQPPzUpJ8hl49AGy&index=46&ab_channel=Codemy.com&t=11m)  
## 修改 models.py
```
python manage.py makemigrations
python manage.py migrate
```

## 測試
在 my_site 下  
```
python manage.py test web_cn
```  
測試報告獲取方法  
1. 安裝  
```
pip install coverage
```  
2. 獲得 coverage  
```
coverage run manage.py test web_cn
coverage report
```
## Docker Compose

Build and Start the Containers
```
docker-compose build
docker-compose up -d
```
Stop the Containers
```
docker-compose down
```
Apply Database Migrations
```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py runserver 0.0.0.0:8000 
```
Create a Superuser
```
docker-compose exec web bash -c "python manage.py migrate && python manage.py createsu"
```
Run the tests within the Docker container
```
docker-compose exec web python manage.py test web_cn
```
Test Coverage Reports
```
docker-compose exec web bash -c "coverage run --source='.' manage.py test web_cn && coverage report"
```
