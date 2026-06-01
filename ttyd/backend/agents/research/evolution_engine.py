def promote_to_production(hypothesis):
    pass


def evolve(hypothesis, score):
    if score > 0.8:
        promote_to_production(hypothesis)
