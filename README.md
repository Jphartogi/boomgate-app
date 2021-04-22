# Boomgate

Boomgate Landing Page

Run python files:
```
1. Create venv
2. Run pip install -r requirements.txt
3. Run python boomgate.py
```

Build .exe file:
```
1. Run pyinstaller --icon="ui/icon/icon.ico" --add-data="ui/icon/icon.ico;." --onefile boomgate.py
2. Copy .exe files on "dist" folder to main directory
3. Delete "build" and "dist" folder
```
> Notes: Change "icon.ico" on with icon on "ui/icon". The path separator is platform-specific, on Windows use `;` while on Linux or Mac use `:`

Docker usage:
```
docker build -t berodimas/boomgate-demo:1.0 -f Dockerfile .
docker pull redis:6.0
docker-compose up -d
```
> Notes: Change display Environtment on [docker-compose.yml](https://git.qlue.id/dimas.adrian/boomgate/blob/master/docker-compose.yml) 