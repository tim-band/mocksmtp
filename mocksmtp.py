import smtpd
import http.server
import asyncore
import sys

class MailTableResponder(http.server.BaseHTTPRequestHandler):
    """HTTP request handler reporting all received emails in a table"""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.server.renderPage().encode("utf-8"))


class MockSMTPServer(smtpd.SMTPServer, http.server.HTTPServer):
    """A mock smtp server"""

    def __init__(self, smtp_address, smtp_port, http_address, http_port):
        smtpd.SMTPServer.__init__(self, (smtp_address, smtp_port), None)
        http.server.HTTPServer.__init__(self, (http_address, http_port), MailTableResponder)
        self.bodyTop = """<!DOCTYPE html>
<meta charset="UTF-8">
<html>
<body>
<h1>Received messages:</h1>
<table>
<tr><th>ID</th><th>From</th><th>To</th><th>Contents</th></tr>
</table>
</body>
</html>
"""
        self.bodyBottom = """</table>
</body>
</html>
"""
        self.emails = []
        self.currentId = 0

    def renderTos(self, tos):
        r = "<ul>"
        for t in tos:
            r += "<li>" + t + "</li>"
        return r + "</ul>"

    def renderRow(self, email):
        return ("<tr><td class='id'>{0}</td>"
            + "<td class='from'>{1}</td>"
            + "<td class='to'>{2}</td>"
            + "<td class='body-text'>{3}</td></tr>").format(
            email.id, email.frm, renderTos(email.tos), email.body)

    def renderPage(self):
        r = self.bodyTop
        for e in self.emails:
            r += renderRow(e)
        return r + self.bodyBottom

    def addEmail(self, frm, tos, body):
        self.currentId += 1
        self.emails.append({
            id: self.currentId,
            frm: frm,
            tos: tos,
            body: body
        })

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        self.responder.addEmail(mailfrom, rcpttos, data)


if __name__ == "__main__":
    smtp_address = '0.0.0.0'
    smtp_port = 25
    http_address = '0.0.0.0'
    http_port = 80
    if 1 < len(sys.argv):
        smtp_address = 'localhost'
        smtp_port = sys.argv[1]
        if 2 < len(sys.argv):
            http_address = 'localhost'
            http_port = sys.argv[2]
    print("Webmail on port {0}, SMTP on port {1}."
        .format(http_port, smtp_port))
    smtp_server = MockSMTPServer(
        smtp_address, int(smtp_port), http_address, int(http_port))
    smtp_server.serve_forever()
