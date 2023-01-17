# TARS-Server
### Twitcasting Autonomous Recording System [Server]
___

## Getting Started
__[TARS-Outpost](https://github.com/quadseed/TARS-Outpost) is required to use the automatic recording feature__
### System Requirements
- Docker Engine

### Set environment variable
Rename `.env.sample` to `.env` and fill in the required information

| Parameter                 | Description                    |
|---------------------------|--------------------------------|
| PORT                      | Web API Server listen port     |
| USER_AGENT                | Web request user agent         |
| NOTIFICATION_SERVER_URL   | TARS-Outpost URL   (Websocket) |
| NOTIFICATION_SERVER_TOKEN | TARS-Outpost Server Token      |
| CLIENT_ID                 | Twitcasting App Client ID      |
| CLIENT_SECRET             | Twitcasting App Client Secret  |

### Run Server
```shell
$ docker-compose up
```

## API Reference
### Recordings
- GET `/records`  
Get information on ongoing recordings


- POST `/records/<user_name>`  
Start recording for the specified user


- DELETE `/records/<user_name>`  
Stop recording for the specified user


### Subscriptions
- GET `/subscriptions`  
Get information on automatic recording targets


- POST `/subscriptions/<user_name>`  
Add specified user to automatic recording list


- DELETE `/subscriptions/<user_name>`  
Remove specified user from automatic recording list


For more information, see `http://<your-server>/docs`
