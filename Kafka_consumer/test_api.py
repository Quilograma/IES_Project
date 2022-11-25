import requests
from requests.auth import HTTPDigestAuth

url = 'http://myapp:5000/Visitors'
r = requests.get(url, auth=HTTPDigestAuth('john', 'hello'),
                 timeout=10)
print(r.status_code)
print(r.headers)
print(type(r.text))
print(r.text)