#!/usr/bin/env python3
import os
import re
import sys
from collections import Counter

if len(sys.argv) < 2:
    print("Usage: udp_pid_detail.py <pid>", file=sys.stderr)
    sys.exit(1)

pid = sys.argv[1]
fd_dir = f"/proc/{pid}/fd"

if not os.path.isdir(fd_dir):
    print(f"PID {pid} not found", file=sys.stderr)
    sys.exit(1)

# 1) Collect all socket inodes for this PID
socket_inodes = set()

for name in os.listdir(fd_dir):
    path = os.path.join(fd_dir, name)
    try:
        target = os.readlink(path)
    except OSError:
        continue

    m = re.match(r"socket:\[(\d+)\]", target)
    if m:
        socket_inodes.add(m.group(1))

if not socket_inodes:
    print(f"No sockets found for PID {pid}")
    sys.exit(0)

def hex_to_ip_port(h):
    ip_hex, port_hex = h.split(":")
    # ip_hex is little endian, e.g. 0100007F -> 127.0.0.1
    bytes_le = [int(ip_hex[i:i+2], 16) for i in (0, 2, 4, 6)]
    bytes_be = list(reversed(bytes_le))
    ip = ".".join(str(b) for b in bytes_be)
    port = int(port_hex, 16)
    return ip, port

entries = []

# 2) Parse /proc/net/udp and match inodes
with open("/proc/net/udp") as f:
    next(f)  # skip header
    for line in f:
        parts = line.split()
        if len(parts) < 10:
            continue
        local_hex = parts[1]
        remote_hex = parts[2]
        inode = parts[9]

        if inode not in socket_inodes:
            continue

        local_ip, local_port = hex_to_ip_port(local_hex)
        remote_ip, remote_port = hex_to_ip_port(remote_hex)
        entries.append((local_ip, local_port, remote_ip, remote_port))

total = len(entries)
print(f"Total UDP IPv4 sockets for PID {pid}: {total}\n")

# 3) Group by local port
by_local_port = Counter()
for lip, lport, rip, rport in entries:
    by_local_port[lport] += 1

print("Counts per local UDP port:")
for port, cnt in sorted(by_local_port.items(), key=lambda x: -x[1]):
    print(f"{cnt:4d}  port {port}")

print("\nDetailed entries:")
for lip, lport, rip, rport in entries:
    print(f"{lip}:{lport} -> {rip}:{rport}")