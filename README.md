# Certificate Retriever

A script to create a key pair and ask for certificate signature on dojot

To use MQTT TLS in Dojot, you need to generate a certificate for each device, sign with EJBCA, making a request to Dojot, and finally when making a publication send the certificates.

## Requirements and Dependencies

- The script works on both Windows and Linux operating systems

- Python 3+
  - Installation :
    - Linux: ```sudo apt install python3-pip```
    - Windows : <https://www.python.org/downloads/>
- Pyopenssl
  - Installation :
    - Linux: ```pip3 install pyopenssl```
    - Windows : ```python3 -m pip install pyopenssl```
- PyJWT
  - Installation :
    - Linux: ```pip3 install PyJWT```
    - Windows : ```python3 -m pip install PyJWT```
- Requests
  - Installation :
    - Linux: ```pip3 install requests```
    - Windows : ```python3 -m pip install requests```

## How to use

### Initial Notes

- The value `<idDevice>` is the **device ID**.

- The value `<userDojot` is **tenant**. If not specified, it will be requested by the script as well as the user's password.

- The URL `<http://hostDojot:port>` is the **address** of the dojot. If the host or host is **https** just do not specify the **http**.

- The `8883` port is the MQTT secure port by default, but it could be another depending on the deployment, in dojot's official `docker-compose` is `8883`. In "unsafe" mode is port `1883`. To check, just look for an `ALLOW_UNSECURED_MODE` variable in the `docker-compose` file. If it has **true** the port is `1883` and you will not need **TLS**, that is, certificates.

### Steps

```console
# Clone the project
git clone https://github.com/ErnandesAJr/certificate-retriever.git

# Enter the "certificate-retriever" folder
computer@name:~/ cd certificate-retriever

# Create the certs folder
computer@name:~/ mkdir certs

# Run the script
computer@name:~/ python3 generateLoginPwd.py <http://hostDojot:port> <idDevice> -u <userDojot>

```

### Example of using the script

```console
# Running the script

computer@name:~/certificate-retriver$ python3 generateLoginPwd.py http://localhost:8000 339e11
enter your dojot usrname : admin
enter password for admin :
Authenticated
CA certificates retrieved
admin:339e11.key pair created at ./certs//admin-339e11.key
339e11 certificate signed. Avaliable at ./certs//admin-339e11.crt
computer@name:~/certificate-retriver$

# View the generated certificates
# Enter certs folder
computer@name:~/certificate-retriver$ cd certs
# List what is inside the folder
computer@name:~/certificate-retriver/certs$ ls # Or dir if windows
IOTmidCA.crt  admin-339e11.crt  admin-339e11.csr  admin-339e11.key
computer@name:~/certificate-retriver/certs$
```

### Example of how to publish with `mosquitto_pub` with the certificates

```console
# sudo apt-get install mosquitto-clients #if necessary

# Enter certs folder # if you are not inside
computer@name:~/certificate-retriver$ cd certs

# Publish to the same device that created the certificate
computer@name:~/certificate-retriver/certs$ mosquitto_pub -h localhost -p 8883 -t /admin/339e11/attrs  -m '{"temperature":10.6.3}' -i admin:339e11 --cert admin-339e11.crt --key admin-339e11.key --cafile IOTmidCA.crt -d
Client admin:339e11 sending CONNECT
Client admin:339e11 received CONNACK (0)
Client admin:339e11 sending PUBLISH (d0 ,q0, r0, m1, 'admin/339e11/attrs', ... (20 bytes))
Client admin:339e11 sending DISCONNECT
computer@name:~/certificate-retriver/certs$
```
