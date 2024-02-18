import requests
import json
import os

from io import StringIO

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit, parse_qsl

hostname = ""
port = 8080

if os.environ.get('MIRROR_HOST') is not None:
    hostname = os.environ['MIRROR_HOST']
    print("Mirror hostname \"{}\" was supplied.".format(hostname))
else:
    print("No hostname supplied by MIRROR_HOST. Falling back to \"{}\"".format(hostname))

if os.environ.get('MIRROR_PORT') is not None:
    port = int(os.environ['MIRROR_PORT'])
    print("Mirror port {} was supplied.".format(port))
else:
    print("No port supplied by MIRROR_PORT. Falling back to {}".format(port))


class MirrorHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Retrieve and parse GET-parameters
        get_params = dict(parse_qsl(urlsplit(self.path).query))
        project_url = sanitize_url(get_params['project'])
        name = get_params['name']

        print("Requesting project '{}' with name '{}'".format(project_url, name))
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(format_data(retrieve_data(project_url), name), "utf-8"))


# Cleans up a kickstarter-url to match the requirements (no GET-params and trailing slash)
def sanitize_url(url):
    url = url.split('?')[0]
    if not url.endswith('/'):
        return url + "/"
    return url


# Loads the current project-data from the kickstarter api
def retrieve_data(project_url):
    url = project_url + "stats.json?v=1"
    headers = {'User-Agent': 'Kickstarter Prometheus Exporter'}
    data = requests.get(url, headers=headers)
    return json.load(StringIO(data.text))


# formats project-data into prometheus-readable format
def format_data(data, name):
    return "{}\n{}\n".format(format_gauge(name + "_money_total", data['project']['pledged'],
                                        "the amount of raised money of " + name),
                           format_gauge(name + "_backers_total", data['project']['backers_count'],
                                        "the amount of backers of " + name))


# Formats a name and data as a prometheus gauge
def format_gauge(name, value, help_text="a gauge"):
    return "# HELP {} {}\n# TYPE {} gauge\n{} {}".format(name, help_text, name, name, value)


if __name__ == '__main__':
    # Create and start web-server
    webServer = HTTPServer((hostname, port), MirrorHTTPServer)
    print("Starting webserver!")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Stopped!")
