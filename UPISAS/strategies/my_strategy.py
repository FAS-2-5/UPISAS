import time

from UPISAS.strategy import Strategy

SERVICE = "RESTAURANT-SERVICE"
IMPLEMENTATION = "restaurant-service"
# A new instance can take over 90 s to register, so keep a spare running ahead of any failure.
DESIRED_INSTANCES = 2
COOLDOWN_SECONDS = 120


class MyStrategy(Strategy):
    """Keeps a spare RESTAURANT-SERVICE instance so that losing one doesn't stop ordering."""

    def __init__(self, exemplar):
        super().__init__(exemplar)
        self.last_add = float("-inf")

    def analyze(self):
        latest = self.knowledge.monitored_data["services"][-1]
        # The service disappears from the monitored data once its last instance is gone.
        service = latest.get(SERVICE)
        instances = service["instances"] if service else []
        return len(instances) < DESIRED_INSTANCES

    def plan(self):
        now = time.monotonic()
        # A new instance takes a while to register, so don't start another one meanwhile.
        if now - self.last_add < COOLDOWN_SECONDS:
            return False
        self.last_add = now
        self.knowledge.plan_data = {
            "operation": "addInstances",
            "parameters": {
                "serviceImplementationName": IMPLEMENTATION,
                "numberOfInstances": 1,
            },
        }
        return True
