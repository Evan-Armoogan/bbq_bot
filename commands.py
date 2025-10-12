from pathlib import Path


def get_main_file_path() -> Path:
    import __main__
    main_file = getattr(__main__, "__file__", None)
    if main_file:
        return Path(main_file).resolve()


class Commands:
    def __init__(self, prefix) -> None:
        commands_dir = get_main_file_path().parent / 'commands'
        files = [p for p in commands_dir.glob("*") if p.is_file()]
        self.commands = [f.stem for f in files]
        self.command_help = {f.stem: f.read_text() for f in files}
        self.prefix = prefix

    def help_arg(self, command: str) -> str:
        return self.command_help.get(command)
    
    def help(self) -> str:
        return '\n'.join(f'**{self.prefix}{cmd}:** {self.command_help.get(cmd)}' for cmd in self.commands)

    commands: list[str]
    command_help: dict[str, str]
    prefix: str
