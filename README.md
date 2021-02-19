# MockSMTP

Selenium-friendly mock SMTP server.

To run the server on port 8025 (to send SMTP traffic
to) and port 8080 (as the HTTP port for webmail), you
can try the following:

```sh
pip install aiosmtpd
python3 mocksmtp.py 8025 8080
```

Or with Docker:

```sh
docker run --rm -i -p 8025:25 -p 8080:80 timband/mocksmtp
```

Any GET request to the HTTP port (8080 in this example)
returns an HTML document containing a table with four columns, like this:

ID | From | To | Contents
---|---|---|---
integer ID (0 for the earliest email, incremented each time) | From address | To addresses, as *li* elements of *ul* | Body text, as *p*-separated lines. HTML tags are neutered, except for *a* links.

The emails are listed most recent first, so that the first
email listed is usually the one you want in your tests.

The *td* elements in the first column have the class
*id", in the second column they have "from", in the
third "to" and in the fourth "body-text".
