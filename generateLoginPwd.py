#!/usr/bin/python
#
import os
import sys
import binascii
from OpenSSL import crypto
from time import sleep
import requests
import getpass

import certUtils
from parseArgs import parseArgs
import conf


# a generic RequestError Exception
class RequestError(Exception):
    def __init__(self, errorCode, message):
        self.message = message
        self.errorCode = errorCode


def dojotLogin(dojot, username, httpsVerify):
    if not username:
        username = input('enter your dojot username: ')
    passwd = getpass.getpass('enter password for ' + username + ': ')
    r = requests.post(dojot + conf.authpath, verify=httpsVerify,
                      json={
                             "username": username,
                             "passwd": passwd
                           })
    if r.status_code != 200:
        print('Authentication faied')
        if err.errorCode in [403, 401]:
            print('Wrong user or password')
        else:
            print('Err code %d. mesage %s' % (r.status_code, err.text))
        exit(-1)
    return r.json()['jwt']


def generateKeys(devname, length, overwrite):
    filename = conf.certsDir + "/" + devname + ".key"
    if not os.path.isfile(filename) or overwrite:
        certUtils.generatePrivateKey(filename, length)
        print(devname + " key pair created at " + filename)
    else:
        print("Key pair already exists at " + filename + ". Skiping.")


def generateCSR(devname, overwrite, dns, ip):
    filename = conf.certsDir + "/" + devname + ".csr"
    if not os.path.isfile(filename) or overwrite:
        certUtils.generateCSR(
                CName=devname,
                privateKeyFile=conf.certsDir + "/" + devname + ".key",
                csrFileName=filename,
                dnsname=dns, ipaddr=ip)
    else:
        print("CSR file already exists at " + filename + ". Skiping.")


def askCertSign(ejbcaHost, devname):
    filename = conf.certsDir + "/" + devname + ".crt"
    if not os.path.isfile(filename) or overwrite:
        try:
            cert = certUtils.signCert(ejbcaHost,
                                      conf.certsDir + "/" + devname + ".csr",
                                      devname, 'dojot')
        except certUtils.EJBCARESTException as err:
            print("Cant sign the CRT. EJBCA-REST return code: "
                  + str(err))
            exit(-1)
        certUtils.saveCRT(filename, cert)
        print(devname + " certificate signed. Avaliable at " + filename)
    else:
        print("Certificate file already exists at " + filename + ". Skiping.")


def retrieveCAChain(ejbcaHost, caName, overwrite):
    filename = conf.certsDir + "/" + caName + ".crt"
    if not os.path.isfile(filename) or overwrite:
        try:
            rawCrt = certUtils.retrieveCAChain(ejbcaHost, caName)
            certUtils.saveCRT(filename, rawCrt)
            print("CA certificates retrieved")
        except KeyError:
            print("Invalid answer returned from EJBCA.")
            exit(-1)
    else:
        print("CA Certificate file already exists at "
              + filename + ". Skiping.")


def retrieveCRL(ejbcaHost, caName):
    try:
        rawCRL = certUtils.retrieveCACRL(ejbcaHost, caName)
    except KeyError:
        print("Invalid answer returned from EJBCA.")
        exit(-1)

    try:
        certUtils.saveCRL(conf.certsDir + "/" + caName + ".crl", rawCRL)
    except crypto.Error:
        print("Could not decode retrieved CRL")
        exit(-1)


if __name__ == '__main__':
    userConf = parseArgs()
    userAuth = dojotLogin(userConf.dojot, userConf.username,
                          userConf.skipHttpsVerification)
    print('Authenticated')

    certUtils.defaultHeader['Authorization'] = 'Bearer ' + userAuth

    retrieveCAChain(userConf.dojot, userConf.caName, userConf.overwrite)
    retrieveCRL(userConf.dojot, userConf.caName)

    generateKeys(userConf.deviceName,
                 userConf.keyLength,
                 userConf.overwrite)

    generateCSR(userConf.deviceName,
                userConf.overwrite,
                userConf.dns, userConf.ip)
    askCertSign(userConf.dojot, userConf.deviceName)

    # deslog
    exit(0)
