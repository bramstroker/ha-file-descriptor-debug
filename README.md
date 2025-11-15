# Home Assistant File Descriptor Debug Tools

This repository provides tools to help Home Assistant users diagnose and solve "OSError: [Errno 24] No file descriptors available" errors. In recent Home Assistant OS versions, a limit on file descriptors was implemented, which can sometimes lead to this error.

## Overview

When Home Assistant runs out of file descriptors, it can cause various components to fail. These tools help you:

1. Monitor file descriptor usage with Home Assistant sensors
2. Identify which types of file descriptors (sockets, pipes, files) are consuming resources
3. Analyze which specific connections might be causing the issue

## Components

### Sensors

The `sensors/sensors.yaml` file contains definitions for Home Assistant sensors that monitor:

- Total file descriptors used by Home Assistant
- Socket file descriptors
- Pipe file descriptors
- Real file descriptors
- TCP IPv4/IPv6 socket counts
- UDP IPv4/IPv6 socket counts

### Diagnostic Scripts

The `scripts` directory contains Python scripts to help identify specific connections:

- `tcp-socket-ips.py`: Analyzes TCP socket connections for a specific process and shows which remote IP addresses have the most connections
- `udp-detail.py`: Analyzes UDP socket connections for a specific process and shows details about local ports and remote endpoints

## Installation

### Sensors

1. Copy the contents of `sensors/sensors.yaml` to your Home Assistant configuration
2. Add the following to your `configuration.yaml`:
   ```yaml
   sensor: !include sensors.yaml
   ```
3. Restart Home Assistant

### Scripts

The scripts need to be run via SSH on the Home Assistant host.
When using Home Assistant OS it's needed to use the `[Advanced SSH & Web Terminal](https://github.com/hassio-addons/addon-ssh)` addon, NOT the default `Terminal & SSH` addon.
This is because the latter is unable to access the home assistant container, which we'll need to further investigate.

1. Disable `Protection mode` toggle for the SSH addon
2. Start the SSH addon when not done already
3. SSH into your Home Assistant system or `Open WebUI` to do it in your browser
4. TODO
5. ..

## Usage

### Monitoring with Sensors

After adding the sensors, you can:

1. Add them to your dashboard to monitor file descriptor usage
2. Set up alerts when values exceed certain thresholds
3. Track trends over time to identify patterns

### Using the Diagnostic Scripts

When you notice high file descriptor usage, you can use the scripts to further investigate:

1. Find the Home Assistant process ID:
   ```bash
   pgrep -f "python3 -m homeassistant"
   ```

2. Analyze TCP connections:
   ```bash
   ./tcp-socket-ips.py <pid>
   ```
   This will show which remote IP addresses have the most TCP connections.

3. Analyze UDP connections:
   ```bash
   ./udp-detail.py <pid>
   ```
   This will show details about UDP sockets, grouped by local port.

## Solving File Descriptor Issues

Once you've identified the source of excessive file descriptors:

1. If a specific integration is causing the issue, consider:
   - Updating the integration
   - Reducing polling frequency
   - Limiting the number of entities

2. If external connections are the problem:
   - Check for network issues causing failed/hanging connections
   - Look for devices repeatedly connecting/disconnecting
   - Consider firewall rules to limit problematic connections

3. System-level solutions:
   - Increase file descriptor limits if possible
   - Restart Home Assistant to clear stale connections
   - Update to the latest Home Assistant version

## Contributing

Contributions to improve these tools are welcome! Please feel free to submit pull requests or open issues with suggestions.