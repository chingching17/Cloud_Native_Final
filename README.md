# Cloud_Native_Final  
## 製作開發環境  
```
docker build -t CN_django_dev .
docker run -it --rm -v ${pwd}:/codeForDev/ CN_django_dev bash # For windows
```