import random

def dumb_ai():
    return {"up": random.choice([True, False]), "down": random.choice([True, False]), "left": random.choice([True, False]), "right": random.choice([True, False]), "brake": random.choice([True, False])}
