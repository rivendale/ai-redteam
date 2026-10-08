"""Developer admin console: edit users and flags against the local database. Development only."""
import http.server

ADMIN_USER = "admin"
ADMIN_PASSWORD = "dev"          # default, printed in the README, changed by nobody
DEBUG = True


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"console (debug on)")


def serve(host, port=8080):
    http.server.HTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    serve("127.0.0.1")
