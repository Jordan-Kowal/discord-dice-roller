FROM python:3.8.9

RUN mkdir /usr/src/app/
WORKDIR /usr/src/app/
COPY .env requirements.txt ./
COPY discord_dice_roller discord_dice_roller
# The `settings` folder will be used as volume in the docker-compose

RUN pip install -r requirements.txt
CMD ["python", "/usr/src/app/discord_dice_roller/main.py"]
