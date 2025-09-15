import re
import os
import subprocess
import argparse
import sys

def infer_func(vmlinux, source_loc):
    gdb_command = f"gdb -q -batch -ex 'file {vmlinux}' -ex 'info line {source_loc}'"
    try:
        output = subprocess.check_output(gdb_command, shell=True, text=True, stderr=open("/dev/null", "w"))
        for line in output.splitlines():
            m = re.search(r'at address 0x[0-9a-fA-F]+ <([\w\d_+<>.-]+)>', output)
            if m:
                # format: func+offset
                funcname = m.group(1)
                # now split and just use func
                funcname = funcname.split("+")[0]
                return funcname
            else:
                raise RuntimeError(f"Cannot infer function name from source location {source_loc}")
    except Exception as e:
        print(f"[!] Error running gdb: {e}", file=sys.stderr)
        sys.exit(1)

def infer_ip(vmlinux, func_name):
    gdb_command = f"gdb -q -batch -ex 'file {vmlinux}' -ex 'disassemble {func_name}'"
    try:
        output = subprocess.check_output(gdb_command, shell=True, text=True, stderr=open("/dev/null", "w"))
        disassembles = output.strip().splitlines()
        for idx, line in enumerate(disassembles):
            if 'call' in line and '__tsan_write' in line:
                for next_line in disassembles[idx+1:]:
                    next_line = next_line.strip()
                    if not next_line or not next_line.startswith('0x'):
                        continue
                    match = re.match(r'(0x[0-9a-fA-F]+)', next_line)
                    if match:
                        ip = match.group(1)
                        return ip
    except Exception as e:
        print(f"[!] Error running gdb: {e}")


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--source_loc", required=True, help="Source location in the format 'file:line'")
    args = argparser.parse_args()

    kernel_dir = os.getenv("KERNEL_DIR", None)
    if not kernel_dir:
        print("[!] Run 'source env.sh' first!")
        sys.exit(1)
    vmlinux = f"{kernel_dir}/vmlinux"
    source_loc = args.source_loc
    func_name = infer_func(vmlinux, source_loc)

    ip = infer_ip(vmlinux, func_name)
    print(ip)

if __name__ == "__main__":
    main()