import re
import os
import subprocess
import argparse
import sys

def get_start_ip(vmlinux, source_loc):
    gdb_command = f"gdb -q -batch -ex 'file {vmlinux}' -ex 'info line {source_loc}'"
    try:
        output = subprocess.check_output(gdb_command, shell=True, text=True, stderr=open("/dev/null", "w"))
        m = re.search(r'at address (0x[0-9a-fA-F]+)', output)
        if m:
            start_ip = m.group(1)
            return start_ip
        else:
            raise RuntimeError(f"Cannot infer IP from source location {source_loc}")
    except Exception as e:
        print(f"[!] Error running gdb: {e}", file=sys.stderr)
        sys.exit(1)

def get_disass(vmlinux, start_ip):
    gdb_command = f"gdb -q -batch -ex 'file {vmlinux}' -ex 'disassemble {start_ip}'"
    try:
        output = subprocess.check_output(gdb_command, shell=True, text=True, stderr=open("/dev/null", "w"))
        disassembles = output.strip().splitlines()
        return disassembles
    except Exception as e:
        print(f"[!] Error running gdb: {e}", file=sys.stderr)
        sys.exit(1)

def get_target_ip(vmlinux, source_loc):
    start_ip = get_start_ip(vmlinux, source_loc)
    disass = get_disass(vmlinux, start_ip)
    found_start = False
    for idx, line in enumerate(disass):
        if start_ip in line:
            found_start = True
        if found_start and 'call' in line and '__tsan_write' in line:
            # return the next instruction address after __tsan_write call
            # find next line with address
            next_line = disass[idx + 1]
            match = re.match(r'^\s*(0x[0-9a-fA-F]+)', next_line)
            if match:
                ip = match.group(1)
                return ip
    return None

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("source_loc", help="Source location in the format 'file:line'")
    args = argparser.parse_args()

    kernel_dir = os.getenv("KERNEL_DIR", None)
    if not kernel_dir:
        print("[!] Run 'source env.sh' first!")
        sys.exit(1)
    vmlinux = f"{kernel_dir}/vmlinux"
    source_loc = args.source_loc
    ip = get_target_ip(vmlinux, source_loc)
    print(ip)

if __name__ == "__main__":
    main()