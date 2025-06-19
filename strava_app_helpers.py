
# Misc helper functions

# BONUS info
points_ECM = [50, 50, 100, 100, 100, 200, 400]  # pts
values_ECM = [25, 50, 100, 200, 300, 500, 1000] # miles

points_RUN = [10, 25, 25, 50,   50,   75,  100, 165] # pts
values_RUN = [1,   3,  5,  8, 13.1, 26.2, 52.4, 105]# miles

points_WALK = [10, 20, 30, 30, 30, 30, 40, 40, 40, 40 ,40] # pts
values_WALK = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100] # miles

points_BIKE = [10, 25, 25, 50, 50,  75,  100, 165] # pts
values_BIKE = [10, 20, 30, 62, 100, 150, 200, 315] # miles

points_SWIM = [10, 25, 25, 50, 50, 75, 100, 165] # pts
values_SWIM = [0.3, 2,  3,  5,  8, 10,  15,  20] # miles

points_LIFT = [10, 25,  25,  50,  50,  75, 100,  165] # pts
values_LIFT = [40, 60, 120, 240, 360, 540, 750, 1000] # minutes

points_ROW = [10,      25,    25,    50,     50,     75,    100,    165] # pts
values_ROW = [7500, 15000, 30000, 60000, 100000, 140000, 180000, 250000] # meters

points_HIIT = [10, 25, 25, 50, 50, 75, 100, 165]
values_HIIT = [15, 30, 45, 75, 100, 150, 200, 300]

class BonusType(enumerate):
    ECM     = 0,
    RUN     = 1, 
    WALK    = 2,
    BIKE    = 3,
    SWIM    = 4,
    LIFT    = 5,
    ROW     = 6,
    HIIT    = 7


def _calc_bonus(pts_arr: list[int], values_arr: list[int], value):
    """Cumulative sum while value < values_arr[x]"""
    return sum([pt for pt,val in zip(pts_arr, values_arr) if val <= value])


def GetBonus(type: BonusType, value: float) -> int:
    match type:
        case BonusType.ECM:
            total = _calc_bonus(points_ECM, values_ECM, value)
        case BonusType.RUN:
            total = _calc_bonus(points_RUN, values_RUN, value)
        case BonusType.WALK:
            total = _calc_bonus(points_WALK, values_WALK, value)
        case BonusType.BIKE:
            total = _calc_bonus(points_BIKE, values_BIKE, value)
        case BonusType.SWIM:
            total = _calc_bonus(points_SWIM, values_SWIM, value)
        case BonusType.LIFT:
            total = _calc_bonus(points_LIFT, values_LIFT, value)
        case BonusType.ROW:
            total = _calc_bonus(points_ROW, values_ROW, value)
        case BonusType.HIIT:
            total = _calc_bonus(points_HIIT, values_HIIT, value)
        case _:
            total = 0
    return total