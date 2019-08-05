# Micropython-DNSServer-Captive-Portal

This is MicroPython script that creates a Wifi AP with both a DNS and Web Server 
that act as a 'Captive Portal' by returning its own IP to all DNS queries in
an attempt to force connecting clients to its Web Server on port 80.  
When connecting from an Android phone it should automatically prompt you to
 'Sign in to the network', which, if clicked, redirects to the Web Server.  If you try
 browsing to a random domain it *should* redirect you to the web server however
 if the request was HTTPS you will just get a Connected Refused error. 

The code is based on several other examples of a MicroPython Captive Portal that I found
on Github however they were 1+ years old and relied on a single loop to accept connection
for both the DNS and Web servers:

- https://github.com/Matt4/micropython-captive-portal-network-setup
- https://github.com/amora-labs/micropython-captive-portal

My version uses asyncio to separate the servers and so can be easily extended with
additional tasks.  Performance and reliability seem better as well.


This was tested with an ESP32 using the latest firmware from https://micropython.org/download#esp32.  
The specific version I tested with was `esp32-20190805-v1.11-187-g00e7fe8ab.bin`.  
This should work with an ESP8266 and others as well but I have not fully tested it.

# Initial Setup (ESP32 only)
Since asyncio is not included in the binary for the ESP32 however it must be installed first.  
Unless you prefer to build your own binary, this requires that your ESP be able to connect 
to the internet to install.
-  Open a python terminal with the ESP32 and use the below to connect to your preferred network:
 ```
import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('yourssid', 'yourpw')
```
- Then run:
```
import upip
upip.install('micropython-uasyncio')
```

# To Do
I'd like to be able to serve HTTPS as well, which would make this a lot more useful however 
I was unable to get the Micropython example code working https://github.com/micropython/micropython/blob/master/examples/network/http_server_ssl.py