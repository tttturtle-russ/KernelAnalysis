TOOLSET = [
            {
                "type": "function",
                "function": {
                    "name": "write_code_to_vm",
                    "description": "Write C code to a file in the VM's shared directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "The name of the file to write to (e.g., 'test.c')."
                            },
                            "code": {
                                "type": "string",
                                "description": "The C code to write to the file."
                            }
                        },
                        "required": ["filename", "code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compile_in_vm",
                    "description": "Compile a C program inside the QEMU VM.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "c_filename": {
                                "type": "string",
                                "description": "The name of the C source file to compile."
                            },
                        },
                        "required": ["c_filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "retrieve_syscall_info",
                    "description": "Retrieve information about a specific syscall from the built-in syscall database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "syscall_name": {
                                "type": "string",
                                "description": "The name of the syscall to retrieve information for (e.g., 'open')."
                            },
                            "ioctl_number_name": {
                                "type": "string",
                                "description": "The ioctl number associated with the syscall, if applicable (e.g., '0x1234'). Optional."
                            }
                        },
                        "required": ["syscall_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_device",
                    "description": "Check and list all available devices in the QEMU VM.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target_directory": {
                                "type": "string",
                                "description": "The directory to check for devices (e.g., '/dev')."
                            }
                        },
                        "required": ["target_directory"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_program_in_vm",
                    "description": "Execute a compiled program inside the QEMU VM.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "executable_name": {
                                "type": "string",
                                "description": "The name of the executable file to run inside the VM, should be an absolute path to the binary."
                            }
                        },
                        "required": ["executable_name"]
                    }
                }
            }
]
