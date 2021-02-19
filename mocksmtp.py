from aiosmtpd.controller import Controller
import http.server
import asyncio
import sys
import itertools
import re

def render_header(header):
    if type(header) is list:
        if len(header) == 0:
            return ""
        r = "<ul>"
        for h in header:
            r += "<li>" + h + "</li>"
        return r + "</ul>"
    return header

emails = []
current_email_id = itertools.count()

class EmailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        data = envelope.content.decode('utf8', errors='replace').splitlines()
        body = []
        headers = {}
        is_body = False
        for d in data:
            if is_body:
                body.append(d)
            else:
                if d == "":
                    is_body = True
                else:
                    kv = d.split(": ")
                    k = kv[0].upper()
                    v = kv[1]
                    if k in headers:
                        if type(headers[k]) is list:
                            headers[k].append(v)
                        else:
                            headers[k] = [headers[k], v]
                    else:
                        headers[k] = v

        e = {
            "id": next(current_email_id),
            "frm": envelope.mail_from,
            "tos": envelope.rcpt_tos,
            "headers": headers,
            "body": body
        }
        emails.append(e)
        return '250 Message accepted for delivery'


class MailTableResponder(http.server.BaseHTTPRequestHandler):
    """HTTP request handler reporting all received emails in a table"""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.server.render_page().encode("utf-8"))


class HttpFrontEnd(http.server.HTTPServer):
    """The web front end for the mock SMTP server"""

    def __init__(self, http_address, http_port):
        http.server.HTTPServer.__init__(self, (http_address, http_port), MailTableResponder)
        self.body_top = """<!DOCTYPE html>
<meta charset="UTF-8">
<html>
<body>
<h1>Received messages:</h1>
<table>
<tr><th>ID</th><th>From</th><th>To</th><th>Cc</th><th>Subject</th><th>Contents</th></tr>
"""
        self.body_bottom = """</table>
</body>
</html>
"""
        self.link_re = re.compile(r"(https?://[^ \t]*)")

    def render_body(self, lines):
        r = []
        for l in lines:
            a = l.replace("&", "&amp;").replace("<", "&lt;")
            r.append(self.link_re.sub(r'<a href="\1">\1</a>', a))
        return "<p>".join(r)

    def render_row(self, email):
        headers = email["headers"]
        if "FROM" in headers:
            frm = headers["FROM"]
        else:
            frm = email["frm"]
        if "TO" in headers:
            tos = headers["TO"]
        else:
            tos = email["tos"]
        if "CC" in headers:
            ccs = headers["CC"]
        else:
            ccs = []
        if "SUBJECT" in headers:
            subject = headers["SUBJECT"]
        else:
            subject = "None"
        return ("<tr><td class='id'>{0}</td>"
            + "<td class='from'>{1}</td>"
            + "<td class='to'>{2}</td>"
            + "<td class='cc'>{3}</td>"
            + "<td class='subject'>{4}</td>"
            + "<td class='body-text'>{5}</td></tr>").format(
            email["id"], render_header(frm), render_header(tos),
            render_header(ccs), render_header(subject),
            self.render_body(email["body"]))

    def render_page(self):
        r = self.body_top
        for e in reversed(emails):
            r += self.render_row(e)
        return r + self.body_bottom


if __name__ == "__main__":
    smtp_address = ""
    smtp_port = 25
    http_address = "0.0.0.0"
    http_port = 80
    if 1 < len(sys.argv):
        smtp_address = "localhost"
        smtp_port = sys.argv[1]
        if 2 < len(sys.argv):
            http_address = "localhost"
            http_port = sys.argv[2]
    print("SMTP on port {0}.".format(smtp_port))
    smtp_server = Controller(EmailHandler(),
        hostname=http_address, port=smtp_port)
    smtp_server.start()
    print("Webmail on port {0}.".format(http_port))
    http_server = HttpFrontEnd(
        http_address, int(http_port))
    http_server.serve_forever()
