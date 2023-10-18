from typing import List
from prisma.models import Rating


def rating_calc(ratings: List[Rating]) -> float:
    return (
        sum(rating.score for rating in ratings) / len(ratings)
        if len(ratings) != 0
        else 0
    )
