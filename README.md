# TARS-Server
### Twitcasting Autonomous Recording System [Server]
[![Build Docker Image](https://github.com/quadseed/TARS-Server/actions/workflows/build.yml/badge.svg)](https://github.com/quadseed/TARS-Server/actions/workflows/build.yml)
___

## Getting Started
__[TARS-Outpost](https://github.com/quadseed/TARS-Outpost) is required to use the automatic recording feature__
### System Requirements
- Docker Engine

### Set environment variable
Rename `.env.sample` to `.env` and fill in the required information

| Parameter                 | Description                                              |
|---------------------------|----------------------------------------------------------|
| PORT                      | Web API Server listen port                               |
| USER_AGENT                | Web request user agent                                   |
| AUTO_RECORDING            | Enable auto-recording feature (TARS-Outpost is required) |
| NOTIFICATION_SERVER_URL   | TARS-Outpost URL   (Websocket)                           |
| NOTIFICATION_SERVER_TOKEN | TARS-Outpost Server Token                                |
| CLIENT_ID                 | Twitcasting App Client ID                                |
| CLIENT_SECRET             | Twitcasting App Client Secret                            |
| DISCORD_WEBHOOK           | Enable Discord Webhook Notification                      |
| DISCORD_WEBHOOK_URL       | Discord Webhook URL                                      |

### Make `docker-compose.yml`
```yaml
version: "3"
services:
  tars-server:
    image: ghcr.io/quadseed/tars-server:latest
    restart: unless-stopped
    volumes:
      - ./outputs/:/app/outputs
      - ./data/:/app/data
    ports:
      - ${PORT}:${PORT}
    environment:
      TZ: Asia/Tokyo
    env_file:
      - .env
```

### Run Server
```shell
$ docker-compose up
```

## API Reference
### Recordings
- GET `/recordings`  
Get information on ongoing recordings


- DELETE `/recordings`  
Stop all ongoing recordings


- POST `/recordings/<user_name>`  
Start recording for the specified user


- DELETE `/recordings/<user_name>`  
Stop recording for the specified user


### Subscriptions
- GET `/subscriptions`  
Get information on automatic recording targets


- POST `/subscriptions/<user_name>`  
Add specified user to automatic recording list


- DELETE `/subscriptions/<user_name>`  
Remove specified user from automatic recording list

### Users
- GET `/users`  
Get detailed information on automatic recording targets



For more information, see `http://<your-server>/docs`
