# MDP2MailService

Клиент для отправки уведомлений.

## Client
Rename `.env.example` to `.env` and edit it to match your environment.
Example of a command to send an email:
`$ python ./cli.py send-async -to "example@mail.ru" -s "Subject of the mail" -m "Message to send" -f "path/to/file.txt"`
