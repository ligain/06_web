
  # IP2W daemon
A simple micro service which shows weather by IP address

## How to run  
You should have `docker` and `docker-compose`  installed before running project.
```  
$ docker-compose --version
docker-compose version 1.8.0, build unknown
$ docker --version
Docker version 1.13.1, build 092cba3
$ git clone https://github.com/ligain/06_web  
$ cd 06_web
$ docker-compose up
```  
Sample request:
```
$ curl http://localhost/ip2w/15.21.187.59/
{
    "city": "Ladera",
    "temp": 26.29,
    "conditions": "туманно"
}
```

## Tests
To run tests ensure that daemon is running:
```
$ python3.6 ip2w.py
$ python3.6 tests.py
```

### Project Goals  
The code is written for educational purposes.