class CustomCounter:
    """
    Counter working with main game loop, 
    works by increment main counter by 1 per every game loop iteration

    Arguments:
    - func: function to be called when object finishes counting
    - fps: number of iterations of main game loop per second
    - time (optional): start time for counter
    - kwargs: arguments for called function
    """
    def __init__(self, _func, _fps: int, _time: float = 1, **kwargs) -> None:
        
        self.func = _func
        self.kwargs = kwargs

        self.counter = 0
        self.flag = False
        self.fps = _fps
        self.time = _time
        self.limit = _time*_fps
        
    def __bool__(self) -> bool:
        return self.flag

    def start(self, time: float | None = None) -> None:
        """
        Start (or restart) counter with new time (or previous if wasn't given)
        """
        if time is not None:
            self.time = time
        self.counter = 0
        self.flag = True
        self.limit = int(self.time*self.fps)
    
    def update(self) -> None:
        """
        Increment counter var, 
        reset counter and run declared function with arguments if equal to time * fps
        """
        self.counter += 1
        if self.counter == self.limit:
            self.flag = False
            self.counter = 0
            self.func(**self.kwargs)

    
