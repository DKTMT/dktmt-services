# DKTMT Services

## Getting start
Add .env file to the project directory 

<details>
<summary>Example .env file</summary>

```
API_GATEWAY_HOST=""
API_GATEWAY_PORT=""
API_GATEWAY_APP_SECRET=""
API_GATEWAY_ALLOWED_HOSTS=""

AUTH_SERVICE_HOST=""
AUTH_SERVICE_PORT=""
AUTH_SERVICE_APP_SECRET=""
AUTH_SERVICE_ALLOWED_HOSTS=""
AUTH_SERVICE_DB_HOST=""
AUTH_SERVICE_DB_PORT=""
AUTH_SERVICE_DB_NAME=""
AUTH_SERVICE_DB_USERNAME=""
AUTH_SERVICE_DB_PASSWORD=""

EXCHANGE_SERVICE_HOST=""
EXCHANGE_SERVICE_PORT=""
EXCHANGE_SERVICE_APP_SECRET=""
EXCHANGE_SERVICE_ALLOWED_HOSTS=""
EXCHANGE_SERVICE_DB_HOST=""
EXCHANGE_SERVICE_DB_PORT=""
EXCHANGE_SERVICE_DB_NAME=""
EXCHANGE_SERVICE_DB_USERNAME=""
EXCHANGE_SERVICE_DB_PASSWORD=""

TASK_HANDLER_SERVICE_HOST=""
TASK_HANDLER_SERVICE_PORT=""
TASK_HANDLER_SERVICE_APP_SECRET=""
TASK_HANDLER_SERVICE_ALLOWED_HOSTS=""
TASK_HANDLER_SERVICE_DB_HOST=""
TASK_HANDLER_SERVICE_DB_PORT=""
TASK_HANDLER_SERVICE_DB_NAME=""
TASK_HANDLER_SERVICE_DB_USERNAME=""
TASK_HANDLER_SERVICE_DB_PASSWORD=""

PREDICT_SERVICE_HOST=""
PREDICT_SERVICE_PORT=""
PREDICT_SERVICE_APP_SECRET=""
PREDICT_SERVICE_ALLOWED_HOSTS=""
PREDICT_SERVICE_DB_HOST=""
PREDICT_SERVICE_DB_PORT=""
PREDICT_SERVICE_DB_NAME=""
PREDICT_SERVICE_DB_USERNAME=""
PREDICT_SERVICE_DB_PASSWORD=""

NOTIFY_SERVICE_HOST=""
NOTIFY_SERVICE_PORT=""

ENCRYPTION_KEY=""
PUBLIC_KEY=""
```
</details>

### Install Docker
Download Docker and follow the installation guide through this [link](https://docs.docker.com/get-docker/)


### Run the services
At the project's root directory
```
docker-compose up -d --build --force-recreate
```
<details>
<summary>Troubleshooting</summary>
    <h4>Docker endpoint for "default" not found (Windows)</h4>
    If the containers couldn't start and return 'docker endpoint for "default" not found' you can delete ~/.docker/contexts/meta/(some sha256)/meta.json. and  restart the Docker desktop
    <br>
    <a href="https://github.com/docker/compose/issues/9956#issuecomment-1294483086">Issue link</a>

</details>
