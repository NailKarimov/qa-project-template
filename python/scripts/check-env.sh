#!/usr/bin/env bash
# Checks the protocol-testing workstation (Linux or WSL2). Read-only: installs nothing.
#   bash scripts/check-env.sh
# Exit code = number of missing required tools.

missing=0
ok()   { printf '  \033[32mok\033[0m    %-14s %s\n' "$1" "$2"; }
miss() { printf '  \033[31mmiss\033[0m  %-14s install: %s\n' "$1" "$2"; missing=$((missing + 1)); }
opt()  { printf '  \033[33mlater\033[0m %-14s %s\n' "$1" "$2"; }

echo "Required now (stage 0-1)"
if command -v python3.12 >/dev/null || python3 -c 'import sys; sys.exit(sys.version_info < (3, 12))' 2>/dev/null; then
  ok python "$(python3 --version 2>&1)"
else
  miss python "sudo apt install python3.12 python3.12-venv  (Ubuntu 24.04 has it)"
fi
command -v git    >/dev/null && ok git "$(git --version)" || miss git "sudo apt install git"
command -v socat  >/dev/null && ok socat "virtual serial ports" || miss socat "sudo apt install socat"
if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
  ok docker "$(docker --version)"
else
  miss docker "Docker Desktop with WSL integration, or: sudo apt install docker.io && sudo usermod -aG docker \$USER"
fi
command -v tshark >/dev/null && ok wireshark "$(tshark --version 2>/dev/null | head -1)" \
  || miss wireshark "sudo apt install wireshark tshark  (on Windows also fine: wireshark.org)"

echo "Required from stage 3 (CAN)"
command -v candump >/dev/null && ok can-utils "candump, cansend" || miss can-utils "sudo apt install can-utils"
if lsmod 2>/dev/null | grep -q '^vcan' || sudo -n modprobe vcan 2>/dev/null; then
  ok vcan "kernel module loads"
else
  opt vcan "sudo modprobe vcan; if it fails on WSL2, use a Linux VM or the Raspberry Pi from stage 4"
fi

echo "Bench (stage 0)"
command -v pulseview >/dev/null && ok pulseview "logic analyzer GUI" \
  || opt pulseview "sigrok.org/wiki/Downloads — on Windows install the Windows build, it sees USB directly"
if ls /dev/ttyUSB* /dev/ttyACM* >/dev/null 2>&1; then
  ok serial "$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | tr '\n' ' ')"
else
  opt serial "no USB serial port yet; on WSL2: usbipd list && usbipd attach --wsl --busid <id>"
fi
if [ -e /dev/ttyUSB0 ] && ! [ -w /dev/ttyUSB0 ]; then
  opt dialout "sudo usermod -aG dialout \$USER, then log in again"
fi

echo
[ "$missing" -eq 0 ] && echo "All required tools are in place." || echo "$missing required tool(s) missing."
exit "$missing"
