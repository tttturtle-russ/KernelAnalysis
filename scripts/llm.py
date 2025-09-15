from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from typing import List, Union
from logger import KALogger as logger
from qemu import QEMU

load_dotenv()

class LLM:
    def __init__(self, 
                 model, 
                 api_key, 
                 base_url,
                 system_prompt,
                 user_prompt: Union[str, List[str]],
                 toolset,) -> None:
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.tools = toolset
        self.tool_map = self._parse_tool_map()
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        self.logger = logger("LLM")
        self.qemu = QEMU()
        if isinstance(user_prompt, str):
            self._log_user(user_prompt)
        elif isinstance(user_prompt, list):
            for user_prompt_chunk in user_prompt:
                self._log_user(user_prompt_chunk)
        with open("builtin_syscalls.json", "r") as f:
            self.syscall_data = json.load(f)

    def _parse_tool_map(self):
        tool_map = {}
        for tool in self.tools:
            tool_name = tool["function"]["name"]
            func = getattr(self, tool_name, None)
            if not func:
                raise ValueError(f"Tool {tool_name} not implemented in LLM class.")
            tool_map[tool_name] = func
        return tool_map

    def _log_user(self, content):
        self.logger.user_log(content)
        self.messages.append({"role": "user", "content": str(content)})

    def _log_assistant(self, content):
        self.logger.assistant_log(content)
        self.messages.append({"role": "assistant", "content": str(content)})

    def _log_tool_call(self, tool_call):
        self.logger.tool_log(json.dumps(tool_call.dict()))
        self.messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            }
        )
    
    def _log_tool_result(self, tool_call_id, result):
        self.logger.tool_result_log(result)
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": "tool-result",
                "content": result
            }
        )

    def shutdown(self, dump_file="log.json"):
        self.dump(dump_file)
        self.qemu.kill()


    def run(self):
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages, # type: ignore
                tools=self.tools,
            )
            message = response.choices[0].message

            if message.content:
                self._log_assistant(message.content)
                if "[DONE]" in message.content:
                    self.logger.info("Final answer received. Terminating.")
                    break

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    self._log_tool_call(tool_call)
                    function_name = tool_call.function.name # type: ignore
                    try:
                        tool = self.tool_map[function_name]
                        arguments = json.loads(tool_call.function.arguments) # type: ignore
                        result = tool(**arguments)
                        self._log_tool_result(tool_call.id, result)
                        self._log_user(result)
                    except (KeyError, json.JSONDecodeError) as e:
                        self._log_tool_result(tool_call.id, f"Invalid tool call: {e}")
                        self._log_user(f"Invalid tool call: {e}")
            
            if not message.tool_calls and not message.content:
                self.logger.info("No further action suggested by the model. Stopping.")
                break

    def write_code_to_vm(self, filename, code):
        shared_dir = os.path.join(os.environ["VM_DIR"], "bin")
        local_filepath = os.path.join(shared_dir, filename)
        try:
            with open(local_filepath, "w") as f:
                f.write(code)
            return f"Successfully wrote code to {filename} in the VM's shared directory."
        except Exception as e:
            return f"Error writing file: {e}"

    def execute_program_in_vm(self, executable_name):
        execute_result = self.qemu.exec_cmd(executable_name)
        return execute_result

    def compile_in_vm(self, c_filename):
        # Path inside the VM
        vm_c_filepath = f"/shared/{c_filename}"
        executable_filename = c_filename.rsplit('.', 1)[0]  # Remove .c extension
        vm_executable_path = f"/shared/{executable_filename}"

        # Compile command
        compile_cmd = f"gcc {vm_c_filepath} -o {vm_executable_path}"
        compile_result = self.qemu.exec_cmd(compile_cmd)
        
        if "STDERR:" in compile_result and "error:" in compile_result.split("STDERR:")[1]:
            return f"Compilation failed:\n{compile_result}"
        return f"Compilation success. Executable at {vm_executable_path}"
    
    def retrieve_syscall_info(self, syscall_name, ioctl_number_name=None):
        if ioctl_number_name:
            key = f"{syscall_name}${ioctl_number_name}"
            if syscall_name in self.syscall_data:
                for entry in self.syscall_data[syscall_name]:
                    if entry["Name"] == key:
                        return json.dumps(entry)
            return f"Syscall {syscall_name} with ioctl number {ioctl_number_name} not found in database."
        if syscall_name == "ioctl":
            ioctls = [ioctl["Name"] for ioctl in self.syscall_data["ioctl"]]
            return f"Available ioctl commands: {', '.join(ioctls)}"
        return json.dumps(self.syscall_data[syscall_name]) if syscall_name in self.syscall_data else "Syscall not found in database."

    def check_device(self, target_directory):
        cmd = f"ls -al {target_directory}"
        result = self.qemu.exec_cmd(cmd)
        return result
    
    def dump(self, filepath):
        message_list = []
        for message in self.messages:
            tmp_message = message.copy()
            if tmp_message["role"] == "assistant" and "tool_calls" in tmp_message:
                tmp_message["tool_calls"] = [tc.dict() for tc in tmp_message["tool_calls"]]
            message_list.append(tmp_message)
        with open(filepath, "w") as f:
            json.dump(message_list, f, indent=4)