import pandas as pd
import numpy as np
from typing import Union

"""
    moneyline <-> probability:
"""


def moneyline_to_prob(s: Union[pd.Series, float]) -> Union[pd.Series, float]:
    return np.where(s > 0, 100 / (s + 100), -s / (100 - s))


def prob_to_moneyline(s: Union[pd.Series, float]) -> Union[pd.Series, float]:
    return np.where(s <= 0.5, 100 / s - 100, 100 * s / (s - 1))


def moneyline_to_prob_spread(s):
    return np.sum(moneyline_to_prob(s)) - 1


"""
    EV + Variance of Bonus bets, etc...
"""


def bonus_bet_ev(
    p: Union[pd.Series, float], spread: float = 0.02
) -> Union[pd.Series, float]:
    return p * (1 / (p + spread) - 1)


def bonus_bet_var(
    p: Union[pd.Series, float], spread: float = 0.02
) -> Union[pd.Series, float]:
    return (p - p**2) * (1 / (p + spread) - 1) ** 2


def profit_boost_ev(
    p: Union[pd.Series, float], boost: float = 0.3, spread: float = 0.06
) -> Union[pd.Series, float]:
    return p * ((1 / (p + spread) - 1) * (1 + boost) + 1) - 1


def profit_boost_var(
    p: Union[pd.Series, float], boost: float = 0.3, spread: float = 0.06
) -> Union[pd.Series, float]:
    return (p - p**2) * ((1 / (p + spread) - 1) * (1 + boost) + 1) ** 2


def no_sweat_ev(
    p: Union[pd.Series, float], bonus_p: float = 0.5, spread: float = 0.06
) -> Union[pd.Series, float]:
    return (
        p * (1 / (p + spread)) + (1 - p) * (bonus_bet_ev(p=bonus_p, spread=spread)) - 1
    )
