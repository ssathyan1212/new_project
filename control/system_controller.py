class SystemController:
    def __init__(self):
        self.state = "NORMAL"

    def update(self, attack_active, collision, recovery_done):
        if collision:
            self.state = "RECOVERY"
        elif recovery_done:
            self.state = "NORMAL"
        elif attack_active:
            self.state = "ATTACK"
        else:
            self.state = "NORMAL"

        return self.state