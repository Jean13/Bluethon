'''
bluethon.py Dependencies
Run: python setup.py
'''

import subprocess, sys


def pip_setup(package):
    try:
        p = subprocess.Popen(["pip", "install", package], stdout = sys.stdout)

        # Print output
        p.communicate()

    except Exception as e:
        print(e)


def apt_setup(package):
    try:
        p = subprocess.Popen(["apt-get", "install", package], stdout = sys.stdout)

        # Print output
        p.communicate()

    except Exception as e:
        print(e)


def uber_install(url, fn):
    try:
        p1 = subprocess.Popen(["wget", url, "-O", fn], stdout = sys.stdout)
        p1.communicate()

        p2 = subprocess.Popen(["tar", "xf", fn], stdout = sys.stdout)
        p2.communicate()

        folder = fn[:-7]

        p3 = subprocess.Popen(["cd", folder], stdout = sys.stdout)
        p3.communicate()

        p4 = subprocess.Popen(["mkdir", "build"], stdout = sys.stdout)
        p4.communicate()

        p5 = subprocess.Popen(["cd", "build"], stdout = sys.stdout)
        p5.communicate()    

        p6 = subprocess.Popen(["cmake", ".."], stdout = sys.stdout)
        p6.communicate()

        p7 = subprocess.Popen(["make"], stdout = sys.stdout)
        p7.communicate()

        p8 = subprocess.Popen(["sudo", "make", "install"], stdout = sys.stdout)
        p8.communicate()

    except Exception as e:
        print(e)


def main():
    apt_list = ["libboost-python-dev", "libboost-thread-dev", "libbluetooth-dev",
                "libglib2.0-dev", "python-dev", "cmake", "libusb-1.0-0-dev",
                "make", "gcc", "g++", "libbluetooth-dev", "pkg-config",
                "libpcap-dev", "python-numpy", "python-pyside", "python-qt4"
                ]

    pip_list = ["gattlib", "numpy", "scapy"]

    for i in apt_list:
        apt_setup(i)

    for j in pip_list:
        pip_setup(j)

    uber_present = raw_input("\nDid you already configure your Ubertooth?\n: ")

    if uber_present == "No" or uber_present == "no" or uber_present == "N" or uber_present == "n":
        uber_install("https://github.com/greatscottgadgets/libbtbb/archive/2017-03-R2.tar.gz", "libbtbb-2017-03-R2.tar.gz")

        uber_install("https://github.com/greatscottgadgets/ubertooth/releases/download/2017-03-R2/ubertooth-2017-03-R2.tar.xz", "ubertooth-2017-03-R2.tar.xz")

    print("[*] Setup complete.\n")


main()

