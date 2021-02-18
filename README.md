# MockSMTP

Selenium-friendly mock SMTP server.

To run the server on port 8025 (to send SMTP traffic
to) and port 8080 (as the HTTP port for webmail), you
can try the following:

```sh
python3 mocksmtp.py 8025 8080
```

Or with Docker:

```sh
docker run --rm -i -p 8025:25 -p 8080:80 timband/mocksmtp
```
