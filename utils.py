from pathlib import Path


def get_main_file_path() -> Path:
    import __main__
    main_file = getattr(__main__, "__file__", None)
    if main_file:
        return Path(main_file).resolve()


def get_pretty_name(name: str) -> str:
    return ' '.join([part.capitalize() for part in name.replace('_', ' ').split()])
