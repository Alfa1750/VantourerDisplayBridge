# Raspberry Pi command reference

This document records shell commands that have been tested on the project's Raspberry Pi environment. Prefer these commands over options that are unavailable in its BusyBox tools.

## Network checks

### Check whether TCP port 5005 is listening

Use:

```sh
netstat -lnt | grep 5005
```

The BusyBox `netstat` on this Pi does **not** support `-p`. Therefore, do not use `netstat -lntp`; it returns:

```text
netstat: invalid option -- 'p'
```

This command shows listening TCP sockets and their local addresses/ports. It does not show the owning process.

## Service management (runit)

The `sv` command is not installed/available on this Pi. Do not use `sv stop`, `sv start`, or `sv status`.

Use these commands instead:

- Check status: `svstat /service/<service-name>`
- Stop: `svc -d /service/<service-name>`
- Start: `svc -u /service/<service-name>`

Example:

```sh
svstat /service/vesmart-server
svc -d /service/vesmart-server
svc -u /service/vesmart-server
```

## VantourerDisplayBridge diagnostics

Follow the service log:

```sh
tail -f /var/log/VantourerDisplayBridge/current
```

Show recent log entries:

```sh
tail -n 60 /var/log/VantourerDisplayBridge/current
```

Search specifically for writes received from the ESP32:

```sh
grep "ESP32 -> Pi" /var/log/VantourerDisplayBridge/current | tail -20
```

The broader search `grep -i "ESP32"` also matches Pi-to-ESP32 notification lines, so it does not isolate incoming ESP32 messages.

Show relevant processes:

```sh
ps | grep -E 'gatt_server|Vantourer|vesmart'
```

## Shutdown

Shut down the Pi cleanly:

```sh
sudo shutdown -h now
```

## Compatibility note

These commands reflect observed behavior on the project's Pi environment. BusyBox applets can differ between systems and firmware versions; do not assume that options available on a full Linux distribution are supported here. When a command fails because an option is unsupported, record the exact error and use a verified BusyBox-compatible alternative.
