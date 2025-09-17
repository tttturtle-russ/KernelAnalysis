import logging
import inspect
import os
from rich.markdown import Markdown
from rich.json import JSON
from rich.console import Console

class KALogger(logging.Logger):
    def __init__(self, name: str, level: int | str = logging.INFO) -> None:
        super().__init__(name, level)
        self.console = Console()
        self.width = self.console.width
       
    def truncate_msg(self, msg):
        if len(msg) > self.width * 30:
            return msg[:self.width * 10] + "\n...[truncated]..."
        return msg   
    
    @property
    def _caller(self):
        # Find the first caller *outside* this class
        stack = inspect.stack()
        for frame_info in stack:
            # Exclude frames from this file or from logging module
            if frame_info.filename != __file__ and not frame_info.filename.endswith("logging/__init__.py"):
                filename = os.path.relpath(frame_info.filename)
                return filename, frame_info.lineno
        return "<unknown>", 0
    
    def user_log(self, msg, *args, **kwargs):
        msg = self.truncate_msg(msg)
        self.console.print("[bold green]USER:[/bold green]")
        self.console.print(Markdown(msg))
        self.console.print("\n")
    
    def assistant_log(self, msg, *args, **kwargs):
        msg = self.truncate_msg(msg)
        self.console.print("[bold magenta]ASSISTANT:[/bold magenta]")
        self.console.print(Markdown(msg))
        self.console.print("\n")
        
    def tool_log(self, msg, *args, **kwargs):
        msg = self.truncate_msg(msg)
        self.console.print("[bold yellow]TOOL CALL:[/bold yellow]")
        try:
            self.console.print(JSON(msg))
        except Exception:
            self.console.print(Markdown(msg))
        finally:
            self.console.print("\n")
    
    def tool_result_log(self, msg, *args, **kwargs):
        msg = self.truncate_msg(msg)
        self.console.print("[bold cyan]TOOL RESULT:[/bold cyan]")
        self.console.print(Markdown(msg))
        self.console.print("\n")
    
    def info(self, msg, *args, **kwargs):
        msg = self.truncate_msg(msg)
        self.console.print("[bold blue]INFO:[/bold blue]")
        self.console.print(Markdown(msg))
        self.console.print("\n")
        
    def warning(self, msg, *args, **kwargs):
        msg = self.truncate_msg(msg)
        self.console.print("[bold yellow]WARNING:[/bold yellow]")
        self.console.print(Markdown(msg))
        self.console.print("\n")

    def error(self, msg, *args, **kwargs):
        msg = self.truncate_msg(msg)
        self.console.print("[bold red]ERROR:[/bold red]")
        self.console.print(Markdown(msg))
        self.console.print("\n")

