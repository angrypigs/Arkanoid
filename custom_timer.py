from threading import Timer



class customTimer:
    """Timer object possible to reset"""

    def __init__(self, time: float, func, args=None) -> None:
        self.time = time
        self.func = func
        self.args = args if args is not None else []
        self.timer = None

    def start(self):
        self.timer = Timer(self.time, self.func, self.args)
        self.timer.daemon = True
        self.timer.start()

    def reset(self):
        if self.timer:
            self.timer.cancel()
        self.start()