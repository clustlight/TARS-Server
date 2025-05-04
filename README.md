# TARS-Server
### Twitcasting Autonomous Recording System [Server]
[![Build Docker Image](https://github.com/clustlight/TARS-Server/actions/workflows/publish-docker-image.yml/badge.svg)](https://github.com/clustlight/TARS-Server/actions/workflows/publish-docker-image.yml)
___

## Getting Started
__[TARS-Outpost](https://github.com/clustlight/TARS-Outpost) is required to use the automatic recording feature__

### Set environment variable
Rename `.env.sample` to `.env` and fill in the required information

| Parameter                 | Description                                              | Default Value                                              | Required |
|---------------------------|----------------------------------------------------------|------------------------------------------------------------|----------|
| PORT                      | Web API Server listen port                               | None                                                       | Yes      |
| USER_AGENT                | Web request user agent                                   | None                                                       | Yes      |
| AUTO_RECORDING            | Enable auto-recording feature (TARS-Outpost is required) | None                                                       | Yes      |
| NOTIFICATION_SERVER_URL   | TARS-Outpost URL (Websocket)                             | None                                                       | No       |
| NOTIFICATION_SERVER_TOKEN | TARS-Outpost Server Token                                | None                                                       | No       |
| CLIENT_ID                 | Twitcasting App Client ID                                | None                                                       | Yes      |
| CLIENT_SECRET             | Twitcasting App Client Secret                            | None                                                       | Yes      |
| DISCORD_WEBHOOK           | Enable Discord Webhook Notification                      | None                                                       | Yes      |
| DISCORD_WEBHOOK_URL       | Discord Webhook URL                                      | None                                                       | No       |
| LOG_FORMAT                | Log message format                                       | `%(asctime)s [%(levelname)s] (%(name)s) >> %(message)s`    | No       |
| SYSLOG_ADDRESS            | Syslog server address                                    | Not set (Syslog disabled)                                  | No       |
| SYSLOG_PORT               | Syslog server port                                       | `514`                                                      | No       |

### Make `compose.yml`
```yaml
services:
  tars-server:
    image: ghcr.io/clustlight/tars-server:latest
    restart: unless-stopped
    volumes:
      - ./outputs/:/app/outputs
      - ./temp/:/app/temp
      - ./data/:/app/data
      - ./logs/:/app/logs
    ports:
      - ${PORT}:${PORT}
    environment:
      TZ: Asia/Tokyo
    env_file:
      - .env
```

### Run Server
```shell
$ docker compose up
```

GUI: `http://<your-server>:${PORT}`

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
