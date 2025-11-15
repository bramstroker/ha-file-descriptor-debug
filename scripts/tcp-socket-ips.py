#!/usr/bin/env python3
import os
import re
import collections
import sys

if len(sys.argv) < 2:
    print("Usage: tcp-socket-ips.py <pid>", file=sys.stderr)
    sys.exit(1)

pid = sys.argv[1]

# Map inode -> remote IPv4 address
inode_to_ip = {}
total_sockets = 0

try:
    with open("/proc/net/tcp") as f:
        next(f)  # skip header
        for line in f:
            parts = line.split()
            if len(parts) < 10:
                continue
            rem_addr = parts[2]  # remote address in hex, like IP:PORT
            inode = parts[9]

            ip_hex, _port_hex = rem_addr.split(':')

            # ip_hex is little-endian hex, e.g. '0100007F' for 127.0.0.1
            # convert to dotted quad
            bytes_le = [int(ip_hex[i:i+2], 16) for i in (0, 2, 4, 6)]
            # reverse to normal order
            bytes_be = list(reversed(bytes_le))
            ip = ".".join(str(b) for b in bytes_be)
            total_sockets += 1
            inode_to_ip[inode] = ip
except FileNotFoundError:
    pass

counts = collections.Counter()

fd_dir = f"/proc/{pid}/fd"
try:
    for name in os.listdir(fd_dir):
        path = os.path.join(fd_dir, name)
        try:
            target = os.readlink(path)
        except OSError:
            continue

        m = re.match(r"socket:\[(\d+)\]", target)
        if not m:
            continue

        inode = m.group(1)
        ip = inode_to_ip.get(inode)
        if ip:
            counts[ip] += 1
except FileNotFoundError:
    print(f"Process {pid} not found")
    raise SystemExit(1)

for ip, cnt in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{cnt:6d} {ip}")

print(f"Total sockets: {total_sockets}")
