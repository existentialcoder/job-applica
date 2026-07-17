class PlanLimitReached(Exception):
    def __init__(self, resource: str, current: int, limit: int, plan: str):
        self.resource = resource
        self.current = current
        self.limit = limit
        self.plan = plan
