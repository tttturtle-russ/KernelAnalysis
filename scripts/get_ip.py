import re
import subprocess
import argparse

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--vmlinux", required=True, help="Path to vmlinux")
    argparser.add_argument("--source_loc", required=True, help="Source location in the format 'file:line'")
    args = argparser.parse_args()

    vmlinux = args.vmlinux
    source_loc = args.source_loc

    gdb_command = "gdb -batch -ex 'file {vmlinux}' -ex 'info line {source_loc}'".format(
        vmlinux=vmlinux,
        source_loc=source_loc
    )

    try:
        output = subprocess.check_output(gdb_command, shell=True, text=True)
        match = re.search(r'starts at address (0x[0-9a-fA-F]+)', output)
        if match:
            ip = match.group(1)
            print(ip)
        else:
            print(f"[!] No address found for {source_loc}")
            print("GDB output:\n" + output)
    except Exception as e:
        print(f"[!] Error running gdb: {e}")

if __name__ == "__main__":
    main()