from apolo_sdk import PluginManager

APOLO_ALL_UPGRADE = """\
You are using Apolo-All {old_ver}, however {new_ver} is available.
You should consider upgrading via the following command:
    pipx upgrade apolo-all
"""


def get_neuro_all_txt(old: str, new: str) -> str:
    return APOLO_ALL_UPGRADE.format(old_ver=old, new_ver=new)


def setup(manager: PluginManager) -> None:
    manager.version_checker.register("apolo-all", get_neuro_all_txt, exclusive=True)
