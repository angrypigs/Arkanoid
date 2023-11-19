import sys
from os import path

def res_path(rel_path: str) -> str:
    """
    Return path to file modified by auto_py_to_exe path if packed to exe already
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = sys.path[0]
    return path.join(base_path, rel_path)

def powerup_index(powerup: str) -> int:
    match powerup:
        case "longer" | "short":
            return 0
        case "fast" | "slow":
            return 1
        case "shield":
            return 2
        case "gun":
            return 3
        case "sticky":
            return 4
        case "blind":
            return 5
        case "multiply":
            return 6
        case _:
            return -1
        
def powerup_value(powerup: str, val: int | None = None) -> float|bool:
    match powerup:
        case "blind" | "sticky" | "shield" | "gun":
            return True
        case "slow":
            return 3
        case "fast":
            return 5
        case "longer":
            return 160
        case "short":
            return 90
        case "multiply":
            return val+2