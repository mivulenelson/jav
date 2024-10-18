import subprocess  # to send commands to windows and change things in windows
import winreg  # writing to Windows registry
import re  # regular expressions
import codecs
from encodings.punycode import adapt
from uaclient.api.u.pro.services.disable.v1 import disable

from xdg.Locale import regex

print("#" * 50)
print("1) Make sure you run this script with administrator privileges")
print("2) Make sure that the WiFi adapter is connected to a network")
print("#" * 50)

mac_to_change_to = ["0A1122334455", "0E1122334455", "021122334455", "061122334455"]

# an empty list to store all the mac addresses
mac_addresses = list()

# we start off by creating expression (regex) for MAC addresses
macAddRegex = re.compile(r"([A-Za-z0-9]{2}[:-]){5}([A-Za-z0-9]{2})")

# we can create a regex for the transport names. It will work in this case
# But when you the .+ or .*, you shd consider making it not as greedy
transportName = re.compile("({.+})")

# we create regex to pick out the adapter index
adapterIndex = re.compile("([0-9]+)")

# python allows us to run system commands by using a function provided by the subprocess module:
getmac_output = subprocess.run("getmac", capture_output=True).stdout.decode().split("\n")

# we loop through the output
for macAdd in getmac_output:
    # we use the regex to find the Mac Addresses
    macFind = macAddRegex.search(macAdd)
    # we use the regex to find the transport name
    transportFind = transportName.search(macAdd)
    # if you dont find a Mac Address or Transport name the option
    if macFind == None or transportFind == None:
        continue
    mac_addresses.append((macFind.group(0), transportFind.group(0)))

print("Which MAC Address do you want to update?")
for index, item in enumerate(mac_addresses):
    print(f"{index} - Mac Address: {item[0]} - Transport Name: {item[1]}")

option = input("Select the menu number corresponding tio the MAC you want to change: ")

while True:
    print("Which MAC address do you want to use? This will change the Network Card's MAC address.")
    for index, item in enumerate(mac_to_change_to):
        print(f"{index} - MAC Address: {item}")

    # prompt the user to select the MAC address they want to change to.
    update_option = input("Select the menu item number corresponding to the new MAC address that you want to change to: ")
    # check to see if the option the user picked is a valid option
    if int(update_option) >= 0 and int(update_option) < len(mac_to_change_to):
        print(f"Your Mac Address will be changed to: {mac_to_change_to[int(update_option)]}")
        break
    else:
        print("You didn't select a valid option. Please try again!")

# we know the first part of the key, we'll append the folders where we'll search the values
controller_key_part = r"SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

# we connect to the HKEY_LOCAL_MACHINE registry. if we specify None
# it means we connect to local machine's refistry
with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
    controller_key_folders = [("\\000" + str(item) if item < 10 else "\\00" + str(item)) for item]
    for key_folder in controller_key_folders:
        try:
            with winreg.OpenKey(hkey, controller_key_part + key_folder, 0, winreg.KEY_ALL_ACCESS) as regkey:
                try:
                    count = 0
                    while True:
                        name, value, type = winreg.EnumValue(regkey, count)
                        count = count + 1
                        if name == "NetCfgInstanceId" and value == mac_addresses[int(option)][1]:
                            new_mac_address = mac_to_change_to[int(update_option)]
                            winreg.SetValueEx(regkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac_address)
                            print("Successly matched Transport Number")
                            break
                except WindowsError:
                    pass
        except:
            pass

run_disable_enable = input("Do you want to disable and reenable your wireless device(s).Press Y or N: ")
if run_disable_enable.lower() == "y":
    run_last_part = True
else:
    run_last_part = False

while run_last_part:
    network_adapters = subprocess.run(["wmic", "nic", "get", "name,index"], capture_output=True).stdout.decode()
    for adpater in network_adapters:
        adapter_index_find = adapterIndex.search(adpater.lstrip())
        if adapter_index_find and "Wireless" in adapter:
            disable = subprocess.run(["wmic", "path", "win32_networkadapter", "where", f"index={adapterIndex}"])
            if(disable.returncode == 0):
                print(f"Enabled {adpater.lstrip()}")

    getmac_output = subprocess.run("getmac", capture_output=True).stdout.decode()
    mac_add = "-".join([(mac_to_change_to[int(update_option)][i:i+1]) for i in range(0, len(mac_to_change_to))])
    if mac_add in getmac_output:
        print("Mac Address Success")
    break
