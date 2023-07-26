import http.server; import requests; import os
from urllib.parse import unquote, parse_qs

memoria={}
formulario='''<!DOCTYPE html><html lang="sp"><meta charset="utf-8">
<title>Bookmark Server</title>
<form method="POST">
    <label>URI larga/original:<input name="urilarga"></label>
    <br>
    <label>Nombre corto:<input name="nombrecorto"></label>
    <br>
    <button type="submit">Guardar</button>
</form>
<p>URIs conocidas:
<pre>{}</pre>'''

def ChecarURI(uri,timeout=5):
  try:
    resp=requests.get(uri,timeout=timeout)
    return resp.status_code==200            # If the GET request returns, was it a 200 OK?
  except requests.RequestException:
    return False                            # If the GET request raised an exception, it's not OK.

class AcortarURL(http.server.BaseHTTPRequestHandler):
  def do_GET(self):                           # A GET request will either be for/(the root path) or for/some-name. Strip off the/and we have either empty string or a name.
    name=unquote(self.path[1:])
    if name:
      if name in memoria:                     # We know that name! Send a redirect to it.
        self.send_response(303)
        self.send_header('Location',memoria[name])
        self.end_headers()
      else:                                   # We don't know that name! Send a 404 error.
        self.send_response(404)
        self.send_header('Content-type','text/plain;charset=utf-8')
        self.end_headers()
        self.wfile.write("No conozco '{}'.".format(name).encode())
    else:
      self.send_response(200)                 # Root path. Send the form.
      self.send_header('Content-type','text/html')
      self.end_headers()                      # List the known associations in the form.
      conocido="\n".join("{} | {}".format(k,memoria[k]) for k in sorted(memoria.keys()))
      self.wfile.write(formulario.format(conocido).encode())
  def do_POST(self):                        # Decode the form data.
    longitud=int(self.headers.get('Content-length',0)) # Decode the form data.
    body=self.rfile.read(longitud).decode()
    params=parse_qs(body)
    urilarga=params["urilarga"][0]
    nombrecorto=params["nombrecorto"][0]
    if ChecarURI(urilarga):
      memoria[nombrecorto]=urilarga         # This URI is good!  Remember it under the specified name.
      self.send_response(303)               # Serve a redirect to the form.
      self.send_header('Location','/')
      self.end_headers()
    else:
      self.send_response(404)               # Didn't successfully fetch the long URI.
      self.send_header('Content-type','text/plain;charset=utf-8')
      self.end_headers()
      self.wfile.write("No se puede fetch la URI '{}'.".format(urilarga).encode())

if __name__=='__main__':
  puerto=int(os.environ.get('PORT',8000))   # Use PORT if it's there.
  dirservidor=('',puerto)
  httpd=http.server.HTTPServer(dirservidor,AcortarURL)
  httpd.serve_forever()

