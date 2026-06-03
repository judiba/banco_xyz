import random


async def generate():
    """
    Generates a hypothesis for the research loop.

    The hypothesis is a dictionary with the following structure:
    {
        "change": "increase_chunk_size" | "decrease_chunk_size" | "change_overlap",
        "value": int
    }
    """
    change_type = random.choice(["increase_chunk_size", "decrease_chunk_size"])
    change_value = random.randint(100, 2000)
    return {"change": change_type, "value": change_value}
