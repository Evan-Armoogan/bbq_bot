from pathlib import Path
from utils import get_main_file_path

class Commands:
    def __init__(self, prefix: str) -> None:
        commands_dir = get_main_file_path().parent / 'commands'
        files = [p for p in commands_dir.glob("*") if p.is_file()]
        self.commands = sorted([f.stem for f in files if f.suffix == '.user'])
        self.commands_admin = sorted([f.stem for f in files if f.suffix == '.admin'])
        self.command_help = {f.stem: f.read_text() for f in files}
        self.command_help_brief = {f.stem: f.read_text().splitlines()[0].strip() for f in files}
        self.prefix = prefix

    def is_admin_command(self, command: str) -> bool:
        return command in self.commands_admin

    def help_arg(self, command: str) -> str:
        return self.command_help.get(command)
    
    def help(self) -> str:
        return '\n'.join(f'**{self.prefix}{cmd}:** {self.command_help_brief.get(cmd)}' for cmd in self.commands)
    
    def help_admin(self) -> str:
        return '\n'.join(f'**{self.prefix}{cmd}:** {self.command_help_brief.get(cmd)}' for cmd in self.commands_admin)

    commands: list[str]
    commands_admin: list[str]
    command_help: dict[str, str]
    command_help_brief: dict[str, str]
    prefix: str
