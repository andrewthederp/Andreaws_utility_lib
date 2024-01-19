def lerp(start, end, t):
    return start + (end - start) * t


class LerpFactory:
    def __init__(self, start, end, lerp_func=lerp):
        self.start = start
        self.end = end

        self.lerp_func = lerp_func

        self.t = 0

    def step(self, amt=0.01):
        self.t += amt
        self.t = min(self.t, 1.0)
        return self.lerp(self.t)

    def lerp(self, t):
        return self.lerp_func(self.start, self.end, t)


def get_percentage(num1, num2):
    return num1 / num2
