import socket
import netifaces

# get a list of all network interfaces
interfaces = netifaces.interfaces()

# iterate over the interfaces and print their IP addresses
for interface in interfaces:
    ifaddr = netifaces.ifaddresses(interface).get(netifaces.AF_INET)
    if ifaddr:
        ifaddr = ifaddr[0]['addr']
        print(f"{interface}: {ifaddr}")