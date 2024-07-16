import socket
import netifaces
import re

def get_private_ip():
    def is_private_ip(ip):
        private_ip_ranges = [
            re.compile(r'^10\.'),
            re.compile(r'^172\.(1[6-9]|2[0-9]|3[01])\.'),
            re.compile(r'^192\.168\.')
        ]
        return any(pattern.match(ip) for pattern in private_ip_ranges)

    try:
        # Attempt to get IP address using socket (online)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))
            private_ip = s.getsockname()[0]
            if is_private_ip(private_ip):
                return private_ip
    except socket.error:
        pass

    # Fallback: Try to get IP address using netifaces (offline)
    try:
        interfaces = netifaces.interfaces()
        for iface in interfaces:
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    private_ip = addr_info['addr']
                    if is_private_ip(private_ip):
                        return private_ip
        print("Private IP not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
