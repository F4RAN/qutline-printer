import socket
import netifaces

def get_private_ip():
    try:
        # Attempt to get IP address using socket (online)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))
            private_ip = s.getsockname()[0]
            return private_ip

    except socket.error:
        # Fallback: Try to get IP address using netifaces (offline)
        try:
            interfaces = netifaces.interfaces()
            for iface in interfaces:
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    private_ip = addrs[netifaces.AF_INET][0]['addr']
                    if private_ip != '127.0.0.1':
                        return private_ip

            print("Private IP not found.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
