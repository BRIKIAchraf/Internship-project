from ipaddress import ip_network
import netifaces, os, platform

def linux_physical_interfaces():
    omit_keywords = ["lo", "virbr", "veth", "vmnet", "vboxnet", "docker", "br-", "tap", "tun"]
    interfaces = [iface for iface in netifaces.interfaces() if not any(keyword in iface for keyword in omit_keywords)]
    active_interfaces = [iface for iface in interfaces if os.system(f"ip link show {iface} up > /dev/null 2>&1") == 0]
    return active_interfaces

def macos_physical_interfaces():
    omit_keywords = ["lo0", "bridge", "gif", "stf", "p2p", "awdl", "utun", "vboxnet", "vmnet"]
    interfaces = [iface for iface in netifaces.interfaces() if not any(keyword in iface for keyword in omit_keywords)]
    active_interfaces = [iface for iface in interfaces if os.system(f"ifconfig {iface} | grep 'status: active' > /dev/null 2>&1") == 0]    
    return active_interfaces

def ubuntu_physical_interfaces():
    import netifaces
    w = netifaces.WMI()
    omit_keywords = ["virtual", "hyper-v", "vmware", "vbox", "virtualbox", "debug"]
    interfaces: list[str] = []
    for nic in w.Win32_NetworkAdapter():
        guid = nic.GUID
        if guid and nic.NetEnabled and not any(
            keyword in doc.lower()
            for keyword in omit_keywords
            for doc in (nic.Name, nic.Description)
        ):
            interfaces.append(guid)
    return interfaces

from typing import List

def physical_interfaces() -> list[str]:
    system_platform = platform.system()
    if system_platform == "Linux":
        return linux_physical_interfaces()
    elif system_platform == "Windows":
        return ubuntu_physical_interfaces()
    elif system_platform == "Darwin":  # macOS
        return macos_physical_interfaces()
    return []

def get_local_network_ranges():
    network_ranges = set[str]()
    for interface in physical_interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for link in addrs[netifaces.AF_INET]:
                ip: str = link["addr"]
                netmask = link["netmask"]
                # Convert IP and netmask to CIDR notation
                network = ip_network(f"{ip}/{netmask}", strict=False)
                network_ranges.add(str(network))
    return list(network_ranges)
