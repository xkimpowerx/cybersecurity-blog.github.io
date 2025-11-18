import http.client

conn = http.client.HTTPSConnection("demo.tradovateapi.com")

payload = {
    "name": "Kwangsun Kim",
    "password": "K!m36692",
    "appId": "string",
    "appVersion": "string",
    "deviceId": "string",
    "cid": "string",
    "sec": "string"
}

headers = {
    'Content-Type': "application/json",
    'Accept': "application/json"
}

conn.request("POST", "/v1/auth/accesstokenrequest", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))