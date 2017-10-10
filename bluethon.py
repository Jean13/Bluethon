'''
Bluethon
Version 0.1

A Bluetooth Low Energy (BTLE) testing tool. 

Options:
    * Discover
    * Sniff
    * Record
    * Decrypt
    * Interact
    * Fuzz

'''

from gattlib import DiscoveryService
import numpy as np
from datetime import datetime
from time import time
import os, subprocess, sys
import re
from scapy.all import fuzz, srbt1, L2CAP_Hdr


'''
Current date in string format.
'''
def time_string():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)

    return year + month + day


'''
Identify vendor associated with a Bluetooth address.
Utilizes Wireshark manuf file for searches.
'''
def get_vendor(btaddr, manuf_file=None):
    # Possible locations of Wireshark manuf file
    file_location=["/etc/manuf",
            "/usr/share/wireshark/wireshark/manuf",
            "/usr/share/wireshark/manuf"]

    if manuf_file:
        file_location = [manuf_file] + file_location

    m_file = None

    for location in file_location:
        m_file = location if os.path.exists(location) else None
        if m_file:
            break

    if not m_file:
        raise Exception

    uap=btaddr.split(':')[2]
    nap=':'.join(btaddr.split(':')[:2])

    if nap == '00:00':
        upper='([0-9A-F]{2}:[0-9A-F]{2}:%s)\s+(\w+)' % (uap.upper())
    else:
        upper='(%s:%s)\s+(\w+)' % (nap.upper(), uap.upper())

    # Open manuf file
    f = open(m_file)
    text = f.read()
    f.close()

    # Search manuf file for matches
    matches = re.findall(upper, text)
    # return matches
    match = [m[1] for m in matches]
    try:
        match = match[0]
    except:
        match = match
    return match


'''
Discover Bluetooth devices' names and addresses.
'''
def discover():

    # Make sure the Bluetooth dongle is running
    p1 = subprocess.Popen(["hciconfig"], stdout = sys.stdout)
    p1.communicate()

    dongle = raw_input("Enter the appropriate hci (E.g., hci1): ")

    p2 = subprocess.Popen(["hciconfig", dongle, "up"], stdout = sys.stdout)
    p2.communicate()

    # Scan time
    scan_time = int(raw_input("Number of seconds to scan for devices (Numbers only): "))

    # X seconds from now
    timeout = time() + scan_time

    # List of discovered devices
    device_list = []

    # Scan for <timeout> seconds
    while True:
        if time() > timeout:
            break

        service = DiscoveryService(dongle)
        devices = service.discover(2)

        for address, name in devices.items():
            print("Name: {} | Address: {}".format(name, address))
            vendor = get_vendor(address)
            device_list.append("Name: {} | Address: {} | Vendor: {}".format(name, address, vendor))

    # List of unique devices
    unique_array = np.unique(device_list)

    # Save discoveries to a timestamped file, including: Name, BTADDR, Vendor
    now = datetime.now()
    current_year = str(now.year)
    current_month = str(now.month)
    current_day = str(now.day)

    latest_scan = current_year + current_month + current_day + "_scan.txt"

    try:
        with open(latest_scan, 'a+') as f:
            for item in unique_array:
                f.write("{}\n\n".format(item))

    except Exception as e:
        print(e)


def wireshark_inform():
    print('[NOTE] Wireshark BTLE Setup:\n \
            1) Click Edit -> Preferences\n \
            2) Click Protocols -> DLT_USER\n \
            3) Click Edit \n \
            4) If "User 0 (DLT=147) is not present, create it \n \
            5) Under "Payload protocol" type: btle \n \
            6) Click Ok -> Ok\n\n')


def wireshark_pipe():
    p1 = subprocess.Popen(["mkfifo", "/tmp/pipe"], stdout = sys.stdout)
    p1.communicate()

    print('[*] Follow these steps to setup Wireshark for piping:\n \
            \t1) Open Wireshark\n \
            \t2) Click Capture -> Options\n \
            \t3) Click Manage Interfaces in the lower right\n \
            \t4) Click Pipes -> +\n \
            \t5) Rename "new pipe" to "/tmp/pipe"\n \
            \t6) Click OK -> Close the window -> Click Start ')

    done = raw_input("Did you follow the instructions above?\n: ")

    p2 = subprocess.Popen(["ubertooth-btle", "-f", "-c", "/tmp/pipe"], stdout = sys.stdout)
    p2.communicate()


def uber_follow(mode, addr=None):
    time = time_string()
    btle = time + "_btle.cap"

    if mode == 'f' or mode == 'F': 
        p1 = subprocess.Popen(["ubertooth-btle", "-f", "-c", btle], stdout = sys.stdout)
        p1.communicate()

    if mode == 'p' or mode == 'P':
        p2 = subprocess.Popen(["ubertooth-btle", "-p", "-c", btle], stdout = sys.stdout)
        p2.communicate()

    if mode == 's':
        p3 = subprocess.Popen(["ubertooth-btle", "-f", "-t" + addr, "-c", btle], stdout = sys.stdout)
        p3.communicate()


def crackle(inp, out, mode=None, ltk=None):
    if mode == "ltk":
        p1 = subprocess.Popen(["crackle", "-i", inp, "-l", ltk,"-o", out], stdout = sys.stdout)
        p1.communicate()

    else:
        p2 = subprocess.Popen(["crackle", "-i", inp, "-o", out], stdout = sys.stdout)
        p2.communicate()


'''
Write data to the target device.
'''
def write_data(addr):
    try:
        data = raw_input("Enter data to be written: ")
        packet = fuzz(L2CAP_Hdr(data))
        srbt1(addr, packet, 0)

    except Exception as e:
        print("\n[!] Error: ")
        print(e)
        print('')


def main():
    print("Bluethon v.0 - A Bluetooth Low Energy (BTLE) testing tool.\n")

    wireshark_inform()

    print('[*] Options:\n \
            1   Discover BTLE devices	[Requires BT dongle]. \n \
            2   Pipe Ubertooth traffic to Wireshark. \n \
            3   Follow connections and save to a capture file. \n \
            4   Follow connections in promiscuous mode and save to a capture file.\n \
            5   Follow a specific device and save to a capture file. \n \
            6   Decrypt BTLE capture files. \n \
            7   Decrypt BTLE capture files with a Long-Term Key (LTK) \n \
            8   Write data to the target device. \n')


    selection = raw_input(': ')

    if selection == '1':
        discover()

    if selection == '2':
        wireshark_pipe()

    if selection == '3':
        uber_follow('f')

    if selection == '4':
        uber_follow('p')

    if selection == '5':
        addr = raw_input("Enter the device address: ")
        uber_follow('s', addr)

    if selection == '6':
        inp = raw_input("Enter the name of the input file: ")
        out = raw_input("Enter the name of the output file: ")

        crackle(inp, out)

    if selection == '7':
        inp = raw_input("Enter the name of the input file: ")
        out = raw_input("Enter the name of the output file: ")
        mode = "ltk"
        ltk = raw_input("Enter the LTK: ")

        crackle(inp, out, mode, ltk)

    if selection == '8':
        addr = raw_input("Enter the device address: ")
        write_data(addr)


main()

