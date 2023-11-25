import sys
from os import path

POWERUP_TYPES = ("blind", "burnball", "fast", "gun", "lifeup", "longer", "multiply",
                 "random", "shield", "short", "slow", "sticky")
POWERUP_DEFAULTS = (120, 4.5, False, False, False, False, 1, False, False)
POWERUP_TIMES = (20, 20, 20, 6, 30, 15, 15, 0, 4.5)

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
    """
    Return powerup's unified index
    """
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
        case "lifeup":
            return 7
        case "burnball":
            return 8
        case _:
            return -1
        
def powerup_value(powerup: str) -> float|bool:
    """
    Return powerup's main value
    """
    match powerup:
        case "blind" | "sticky" | "shield" | "gun" | "lifeup" | "burnball":
            return True
        case "slow":
            return 3.5
        case "fast":
            return 5.5
        case "longer":
            return 160
        case "short":
            return 90
        case "multiply":
            return 2

def pad_index(length: float) -> str:
    """
    Return str from pad length needed to read images from dict
    """
    match length:
        case 90:
            return "2"
        case 160:
            return "1"
        case _:
            return "0"