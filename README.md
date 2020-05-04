# certificate-retriever
A script to create a key pair and ask for certificate signature on dojot

## How use

#### Initial Notes

- The value `5c6512` is the device ID, it must be replaced by the device ID already created in the dojot that will be generated certificates.
- The value `admin` in  `admin:5c6512` is `tenant`, should be replaced if necessary,
- The URL `http://localhost:8000` is the address of the dojot, should be replaced if necessary.
- The host `localhost`, is part of that URL mentioned above
- The `8883` port is the MQTT secure port by default, but it could be another depending on the deployment, in dojot's official `docker-compose` is `8883`.

```console
sudo apt install python3-pip #if necessary

pip3 install crypt
pip3 install pyOpenSSL

mkdir certs

python3 generateLoginPwd.py http://localhost:8000 admin:5c6512
```

Certificates will be in `certs

#### Example of how to publish with `mosquitto_pub` with the certificates:

```
sudo apt-get install mosquitto-clients   #if necessary

cd certs
mosquitto_pub -h localhost -p 32665 -t /admin/5c6512/attrs  -m '{"test_payload":1000}' --cert admin:5c6512.crt --key admin:5c6512.key --cafile IOTmidCA.crt
```