import subprocess
import os
import psutil
from time import sleep
from logger import KALogger as logger

class QEMU:
    def __init__(self) -> None:
        assert os.getenv("VM_DIR"), "[ERROR]: Run source scripts/env.sh first"
        self._vm_dir = str(os.getenv("VM_DIR"))
        self._script = self._vm_dir + "/run_img.sh"
        self._log_file = self._vm_dir + "/.log"
        self._pid_file = self._vm_dir + "/.pid"
        self._shared_dir = self._vm_dir + "/bin"
        self._logger = logger("QEMU")
        self.boot()

    def _check_boot(self):
        for line in self._read_log():
            if self._check_boot_complete(line):
                return True
        return False

    def _read_log(self):
        with open(self._log_file, "r") as f:
            while True:
                where = f.tell()
                line = f.readline()
                if not line:
                    sleep(3)
                    f.seek(where)
                else:
                    yield line.decode('utf-8').strip() if isinstance(line, bytes) else line

    def _check_boot_complete(self, output):
        return "syzkaller login:" in output


    def exec_cmd(self, cmd):
        try:
            cmd = f"ssh -p 2222 -i {self._vm_dir}/image/bullseye.id_rsa root@localhost {cmd}".split()
            self._logger.info(f"Executing command: {cmd}")
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            self._logger.info(f"STDOUT: {p.stdout} \n STDERR: {p.stderr}")
            return f"\nSTDOUT: {p.stdout}\nSTDERR: {p.stderr}" if p.stderr else f"\nSTDOUT: {p.stdout}"
        except subprocess.CalledProcessError as e:
            self._logger.critical(f"{e.output.decode()}")
            return e.output.decode()
        except subprocess.TimeoutExpired as e:
            self._logger.critical(f"Command timeout: {e}")
            return f"Command timeout: {e}"
        

    def kill(self):
        psutil.Process(int(open(self._pid_file).read())).terminate()
        self._logger.info("Terminating QEMU process...")
        sleep(3)
        if os.path.exists(self._pid_file):
            self._logger.critical("Failed to terminate QEMU process...")

    def boot(self):
        subprocess.Popen(self._script, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sleep(2)
        if not self._check_boot():
            self._logger.error("Failed to boot QEMU")
            raise RuntimeError("Failed to boot QEMU")
        self._logger.info("VM booted successfully")

    def reboot(self):
        self.kill()
        self.boot()

    def _process_compile_cmd(self, compile_cmd, num):
        if "-o" in compile_cmd:
            # replace the origin output name to prog
            cmds = compile_cmd.split()
            idx = cmds.index("-o")
            if idx + 1 < len(cmds):
                cmds[idx + 1] = f"/shared/prog{num}"
            return " ".join(cmds)
        else:
            return compile_cmd + f" -o /shared/prog{num}"

    def preprocess(self, program):
        filename1 = program["program_1"]["filename"]
        abs_filename1 = f"{self._shared_dir}/{filename1}"
        compile_cmd1 = program["program_1"]["compile_cmd"]
        compile_cmd1 = compile_cmd1.replace(filename1, f"/shared/{filename1}")
        compile_cmd1 = self._process_compile_cmd(compile_cmd1, 1)

        filename2 = program["program_2"]["filename"]
        abs_filename2 = f"{self._shared_dir}/{filename2}"
        compile_cmd2 = program["program_2"]["compile_cmd"]
        compile_cmd2 = compile_cmd2.replace(filename2, f"/shared/{filename2}")
        compile_cmd2 = self._process_compile_cmd(compile_cmd2, 2)

        program["program_1"]["compile_cmd"] = compile_cmd1
        program["program_2"]["compile_cmd"] = compile_cmd2

        program["program_1"]["filename"] = abs_filename1
        program["program_2"]["filename"] = abs_filename2

        return program

