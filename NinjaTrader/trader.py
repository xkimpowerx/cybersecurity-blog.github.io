import http.client

conn = http.client.HTTPSConnection("demo.tradovateapi.com")

headers = {
    'Accept': "application/json",
    'Authorization': "Bearer 123"
}

conn.request("GET", "/v1/auth/me", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))