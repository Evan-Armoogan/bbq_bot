from pathlib import Path
from discord.ext import commands


def get_main_file_path() -> Path:
    import __main__
    main_file = getattr(__main__, "__file__", None)
    if main_file:
        return Path(main_file).resolve()
