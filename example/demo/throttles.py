from rest_framework.throttling import UserRateThrottle


class HighRateThrottle(UserRateThrottle):
    scope = "high"


class LowRateThrottle(UserRateThrottle):
    scope = "low"
