# MDP2MailService

Сервис отправки уведомлений

## Running FastAPI in dev mode

`$ fastapi dev mdp2mailservice/main.py`

## Client

Example of a command to send an email:
`$ python ./cli.py send-async -to "example@mail.ru" -s "Subject of the mail" -m "Message to send" -f "path/to/file.txt"`

## Docker build

`$ docker build -t mdp2/mailservice .`
