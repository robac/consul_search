class ConsulSearch:
    def __init__(self):
        self.last_update = None
        self.in_progress = False
        self.timer_run = 0

    @property
    def can_process(self):
        return self.last_update and not self.in_progress

    def make_callable(self):
        self.last_update = "xxxx"
        self.timer_run = self.timer_run + 1