import re
from datetime import datetime, timedelta

# In-memory lease storage (could also use cache framework)
ipv4_leases = {}
ipv6_leases = {}

def validate_mac_address(mac):
    """Validate MAC address format"""
    pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
    return bool(re.match(pattern, mac))

def mac_to_bytes(mac):
    """Convert MAC address string to list of integers"""
    return [int(octet, 16) for octet in mac.split(':')]

def bitwise_check_odd_even(mac):
    """Use bitwise operations to check if sum of MAC bytes is odd/even"""
    mac_bytes = mac_to_bytes(mac)
    total = sum(mac_bytes)
    # Bitwise AND with 1 to check if odd (returns 1) or even (returns 0)
    is_odd = total & 1
    return "odd" if is_odd else "even"

def toggle_bit(byte_val, bit_position):
    """Toggle a specific bit in a byte using XOR"""
    return byte_val ^ (1 << bit_position)

def mac_to_eui64(mac, prefix="2001:db8::"):
    """
    Convert MAC address to IPv6 using EUI-64 format
    Toggle 7th bit (universal/local bit) in first octet
    """
    mac_bytes = mac_to_bytes(mac)
    
    # Toggle the 7th bit (universal/local bit)
    mac_bytes[0] = toggle_bit(mac_bytes[0], 6)  # 7th bit is at position 6 (0-indexed)
    
    # Insert FF:FE in the middle
    eui64 = mac_bytes[:3] + [0xff, 0xfe] + mac_bytes[3:]
    
    # Format as IPv6
    ipv6_suffix = ':'.join([
        f'{eui64[i]:02x}{eui64[i+1]:02x}' 
        for i in range(0, len(eui64), 2)
    ])
    
    return f"{prefix}{ipv6_suffix}"

def assign_ipv4(mac):
    """Assign IPv4 address from 192.168.1.0/24 pool"""
    # Check if MAC already has a lease
    if mac in ipv4_leases:
        lease_info = ipv4_leases[mac]
        # Check if lease is still valid
        if datetime.now() < lease_info['expiry']:
            return lease_info['ip']
    
    # Assign new IP
    # Start from .10 to .254 (avoiding network, broadcast, and gateway)
    used_ips = {lease['ip'] for lease in ipv4_leases.values()}
    
    for i in range(10, 255):
        ip = f"192.168.1.{i}"
        if ip not in used_ips:
            # Create lease
            lease_time = 3600  # 1 hour
            ipv4_leases[mac] = {
                'ip': ip,
                'expiry': datetime.now() + timedelta(seconds=lease_time),
                'lease_time': lease_time
            }
            return ip
    
    return None  # Pool exhausted

def assign_ipv6(mac):
    """Assign IPv6 address using EUI-64"""
    # Check if MAC already has a lease
    if mac in ipv6_leases:
        lease_info = ipv6_leases[mac]
        # Check if lease is still valid
        if datetime.now() < lease_info['expiry']:
            return lease_info['ip']
    
    # Generate IPv6 using EUI-64
    ipv6 = mac_to_eui64(mac)
    lease_time = 3600  # 1 hour
    
    ipv6_leases[mac] = {
        'ip': ipv6,
        'expiry': datetime.now() + timedelta(seconds=lease_time),
        'lease_time': lease_time
    }
    
    return ipv6

def assign_ip(mac, dhcp_version):
    """Main function to assign IP based on DHCP version"""
    if not validate_mac_address(mac):
        return None, "Invalid MAC address format"
    
    if dhcp_version == "DHCPv4":
        ip = assign_ipv4(mac)
        lease_dict = ipv4_leases
    elif dhcp_version == "DHCPv6":
        ip = assign_ipv6(mac)
        lease_dict = ipv6_leases
    else:
        return None, "Invalid DHCP version"
    
    if ip is None:
        return None, "No available IP addresses"
    
    lease_time = lease_dict[mac]['lease_time']
    return ip, lease_time
