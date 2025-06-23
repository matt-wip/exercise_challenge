from dataclasses import dataclass, field
from datetime import datetime
from math import floor
from typing import List
import pandas as pd

import strava_app_api
from strava_app_helpers import GetBonus, BonusType
from strava_app_settings import START, END

## Exercise Challenge options
ECM_swim = 9.0
ECM_run = 3.0
ECM_bike = 1.0

pts_per_min = 15.0 / 60.0 # 15 pts / hour exercised 
adventure_points = 10   # pts per 30 min. so, 20 pts/hr

# unique bonuses
bonus_bird = 30         # if exercised on start or end date
bonus_triathlete = 30
bonus_world = 100
bonus_500 = 55
bonus_first_step = 15
bonus_lucky_7s = 100
bonus_adventure_club = 100

## Helper functions
def toAdvPts(time: float):
    """Convert adventure activity time to points.
    
    Args:
        time: Adventure activity time in minutes
        
    Returns:
        Points earned for the activity
    """
    return floor(time / 30) * adventure_points

def round_all(dataclass_obj: dataclass, ndigits=2):
    """Rounds all floats in dataclass to ndigits.
    
    Args:
        dataclass_obj: The dataclass object to round
        ndigits: Number of decimal places to round to
    """
    for f_name, f_obj in dataclass_obj.__dataclass_fields__.items():
        if f_obj.type is float:
            value = getattr(dataclass_obj, f_name)
            setattr(dataclass_obj, f_name, round(value, ndigits))

## Stats Data Class
@dataclass
class StravaStats:
    """Store metrics retrieved from Strava"""
    total_moving_time: float = 0    # minutes
    swim_distance: float = 0        # miles
    run_distance: float = 0         # miles
    bike_distance: float = 0        # miles
    walk_distance: float = 0        # miles
    weightlift_time: float = 0      # minutes
    stairstepper_time: float = 0    # minutes
    hiit_time: float = 0            # minutes
    rowing_distance: float = 0      # meters
    # adventure categories 
    pickleball_time: float = 0      # minutes
    yoga_time: float = 0            # minutes
    racquetball_time: float = 0     # minutes
    tennis_time: float = 0          # minutes
    soccer_time: float = 0          # minutes
    rock_climb_time: float = 0      # minutes
    surf_time: float = 0            # minutes
    paddleboard_time: float = 0     # minutes
    kayak_time: float = 0           # minutes
    skiing_time: float = 0          # minutes
    badminton_time: float = 0       # minutes
    golf_time: float = 0            # minutes
    # unique categories
    firstOfMonth: bool = False
    lastOfMonth: bool = False


@dataclass
class UserPoints:
    """Store metrics derived from StravaStats"""
    total_points:   int = 0
    total_time_pts: float = 0

    total_ecm:      float = 0
    ecm_bike:       float = 0
    ecm_run:        float = 0
    ecm_walk:       float = 0
    ecm_swim:       float = 0

    bonus_fields:  list[str] = field(default_factory=lambda: 
        ["bonus_ECM", "bonus_swim", "bonus_run", "bonus_walk",
         "bonus_bike", "bonus_lift", "bonus_HIT", "bonus_row"]
    )
    total_bonus:    int = 0
    bonus_ECM:      int = 0
    bonus_swim:     int = 0
    bonus_run:      int = 0
    bonus_walk:     int = 0
    bonus_bike:     int = 0
    bonus_lift:     int = 0
    bonus_HIT:      int = 0
    bonus_row:      int = 0
    
    unique_fields:  list[str] = field(default_factory=lambda: 
        ["early_bird", "final_stretch", "triathlete", "around_the_world",
         "club_500", "first_step", "lucky_7s", "club_adventure"]
    )
    total_unique:   int = 0
    early_bird:     int = 0     # exercised on first day
    final_stretch:  int = 0     # exercised on last day
    triathlete:     int = 0     # did a run, swim, and bike
    around_the_world:   int = 0 # did a: lift, row, stair, hit, and walking
    club_500:       int = 0     # Get 500 points in one activity. ECD does not count
    first_step:     int = 0     # Exercise >60 minutes
    lucky_7s:       int = 0     # >777 ECM
    club_adventure: int = 0     # >6 adventure sports

    adventure_fields :  list[str] = field(default_factory=lambda: [
        "pickleball", "yoga", "racquetball", "tennis", "soccer", 
        "rock_climb", "surf", "kayak", "skiing", "badminton", "golf"
    ])
    total_adventure:    int = 0
    pickleball:     int = 0  
    yoga:           int = 0        
    racquetball:    int = 0 
    tennis:         int = 0      
    soccer:         int = 0      
    rock_climb:     int = 0  
    surf:           int = 0        
    paddleboard:    int = 0 
    kayak:          int = 0       
    skiing:         int = 0      
    badminton:      int = 0   
    golf:           int = 0

    def sumTotalBonus(self) -> int:
        """Calculate total bonus points."""
        return sum(getattr(self, f) for f in self.bonus_fields)
    def sumTotalAdventure(self) -> int:
        """Calculate total adventure points."""
        return sum(getattr(self, f) for f in self.adventure_fields)
    def sumTotalUnique(self) -> int:
        """Calculate total unique achievement points."""
        return sum(getattr(self, f) for f in self.unique_fields)


class UserEC():
    """Stores stats and points for an individual:
        user_id: Strava token user id
        team: team number
        stats:  StravaStats object
        points: UserPoints object
        _has_stats: boolean to check if stats have been calculated
        _has_points: boolean to check if points have been calculated
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.stats  = StravaStats()
        self.points = UserPoints()
        self._has_stats  = False # true if calculate_stats() was run
        self._has_points = False # true if ____() was run

    def calculate_stats(self):
        """ Retrieves user's Strava activities within challenge time window.
            Calculates stats from those activities
        """
        activities = strava_app_api.get_user_activities(self.user_id)
        if not activities:
            return False

        fist_day = START + 86400
        last_day = END - 86400
        for workout in activities:
            distance = workout['distance'] / 1609.3     # meters to miles
            duration = workout['moving_time'] / 60.0    # seconds to minutes
            sport = workout['sport_type'].upper()       # type

            self.stats.total_moving_time += duration

            # Check workout is on first or last day
            date = int(datetime.strptime(workout['start_date'], "%Y-%m-%dT%H:%M:%SZ").timestamp())
            if (date < fist_day):
                self.stats.firstOfMonth = True
            elif (date > last_day):
                self.stats.lastOfMonth = True

            # Get workout distances/times
            match sport:
                case 'SWIM':
                    self.stats.swim_distance += distance
                case 'RUN' | 'VIRTUALRUN' | 'ELLIPTICAL':
                    self.stats.run_distance += distance
                case 'RIDE' | 'VIRTUALRIDE' | 'MOUNTAINBIKERIDE'| 'EMOUNTAINBIKERIDE' | 'GRAVELRIDE':
                    self.stats.bike_distance += distance
                case 'WALK' | 'HIKE':
                    self.stats.walk_distance += distance
                case 'WEIGHTTRAINING' | 'WORKOUT':
                    self.stats.weightlift_time += duration
                case 'STAIRSTEPPER':
                    self.stats.stairstepper_time += duration
                case 'CROSSFIT' | 'HIGHINTENSITYINTERVALTRAINING':
                    self.stats.hiit_time += duration
                case 'ROWING' | 'VIRTUALROW':
                    self.stats.rowing_distance += workout['distance'] # meters
                # Adventure categories
                case 'PICKLEBALL':
                    self.stats.pickleball_time += duration
                case 'YOGA':
                    self.stats.yoga_time += duration
                case 'RACQUETBALL' | 'SQUASH':
                    self.stats.racquetball_time += duration
                case 'TENNIS':
                    self.stats.tennis_time += duration
                case 'SOCCER':
                    self.stats.soccer_time += duration
                case 'ROCKCLIMBING':
                    self.stats.rock_climb_time += duration
                case 'SURFING':
                    self.stats.surf_time += duration
                case 'STANDUPPADDLING':
                    self.stats.paddleboard_time += duration
                case 'KAYAKING' | 'CANOEING':
                    self.stats.kayak_time += duration
                case 'ALPINESKI' | 'BACKCOUNTRYSKI' | 'NORDICSKI' | 'ROLLERSKI':
                    self.stats.skiing_time += duration
                case 'BADMINTON':
                    self.stats.badminton_time += duration
                case 'GOLF':
                    self.stats.golf_time += duration

        self._has_stats = True
        return True
    # end calculate_stats()
    
    def calculate_points(self):
        """Generates individual's points from Strava stats.
        Runs 'calculate_stats()' if not run yet """
        if not self._has_stats:
            if not self.calculate_stats(): # calls Strava API
                return None
        
        # Calculate ECM
        self.points.ecm_bike    = ECM_bike * self.stats.bike_distance
        self.points.ecm_swim    = ECM_swim * self.stats.swim_distance
        self.points.ecm_walk    = ECM_run  * self.stats.walk_distance
        self.points.ecm_run     = ECM_run  * self.stats.run_distance
        self.points.total_ecm = sum([self.points.ecm_bike, self.points.ecm_swim,
                                     self.points.ecm_walk, self.points.ecm_run])

        # Calculate Bonus Points
        self.points.bonus_ECM   = GetBonus(BonusType.ECM,  self.points.total_ecm)
        self.points.bonus_swim  = GetBonus(BonusType.SWIM, self.stats.swim_distance)
        self.points.bonus_run   = GetBonus(BonusType.RUN,  self.stats.run_distance)
        self.points.bonus_walk  = GetBonus(BonusType.WALK, self.stats.walk_distance)
        self.points.bonus_bike  = GetBonus(BonusType.BIKE, self.stats.bike_distance)
        self.points.bonus_lift  = GetBonus(BonusType.LIFT, self.stats.weightlift_time)
        self.points.bonus_HIT   = GetBonus(BonusType.HIIT, self.stats.hiit_time)
        self.points.bonus_row   = GetBonus(BonusType.ROW,  self.stats.rowing_distance)

        # Calculate Unique Points
        self.points.early_bird    = bonus_bird if self.stats.firstOfMonth else 0
        self.points.final_stretch = bonus_bird if self.stats.lastOfMonth  else 0
        isTriathlete = all([
            (self.stats.swim_distance > 0),
            (self.stats.bike_distance > 0),
            (self.stats.run_distance  > 0)
        ])
        self.points.triathlete = bonus_triathlete if isTriathlete else 0

        isWorldTraveler = all([
            (self.stats.weightlift_time > 0),
            (self.stats.rowing_distance > 0),
            (self.stats.stairstepper_time > 0),
            (self.stats.hiit_time > 0),
            (self.stats.walk_distance > 0)
        ])
        self.points.around_the_world = bonus_world if isWorldTraveler else 0

        is500Club = any([True for bon in self.points.bonus_fields if (bon != "bonus_ECM" and getattr(self.points, bon) >= 500)])
        self.points.club_500    = bonus_500        if is500Club                          else 0
        self.points.first_step  = bonus_first_step if self.stats.total_moving_time >= 60 else 0
        self.points.lucky_7s    = bonus_lucky_7s   if self.points.total_ecm >= 777       else 0

        # Calculate Adventure Points
        self.points.pickleball  = toAdvPts(self.stats.pickleball_time)
        self.points.yoga        = toAdvPts(self.stats.yoga_time)
        self.points.racquetball = toAdvPts(self.stats.racquetball_time)
        self.points.tennis      = toAdvPts(self.stats.tennis_time)
        self.points.soccer      = toAdvPts(self.stats.soccer_time)
        self.points.rock_climb  = toAdvPts(self.stats.rock_climb_time)
        self.points.surf        = toAdvPts(self.stats.surf_time)
        self.points.kayak       = toAdvPts(self.stats.kayak_time)
        self.points.skiing      = toAdvPts(self.stats.skiing_time)
        self.points.badminton   = toAdvPts(self.stats.badminton_time)
        self.points.golf        = toAdvPts(self.stats.golf_time)
        number_of_adventures = sum(1 for adv in self.points.adventure_fields if (getattr(self.points, adv) > 0))
        self.points.club_adventure = 100 if (number_of_adventures >= 6) else 0

        # Calculate Total Points
        self.points.total_time_pts  = self.stats.total_moving_time * pts_per_min
        self.points.total_bonus     = self.points.sumTotalBonus()
        self.points.total_unique    = self.points.sumTotalUnique()
        self.points.total_adventure = self.points.sumTotalAdventure()
        
        self.points.total_points = sum([
            self.points.total_time_pts,
            self.points.total_bonus,
            self.points.total_unique,
            self.points.total_adventure
        ])

        # Finally
        round_all(self.points)
        self._has_points = True
        return True
    

def create_dataframe_from_users(user_results: List) -> pd.DataFrame:
    """Convert list of UserEC objects to pandas DataFrame efficiently.
    
    Args:
        user_results: List of UserEC objects
        
    Returns:
        pd.DataFrame: DataFrame containing user data
    """
    data_rows = [None] * len(user_results)
    index = 0
    
    for user in user_results:
        row = {
            'User_ID': user.user_id,
            'Team': 0,
            'Rank': 0,
            'Name': "None",
            'Total_Points': user.points.total_points,
            'Moving_Time': user.stats.total_moving_time,
            'Time_Points': user.points.total_time_pts,
            'Bonus_Points': user.points.total_bonus,
            'Unique_Points': user.points.total_unique,
            'Adventure_Points': user.points.total_adventure,
            # Activity distances
            'Net_ECM': user.points.total_ecm,
            'Run_Distance': user.stats.run_distance,
            'Walk_Distance': user.stats.walk_distance,
            'Bike_Distance': user.stats.bike_distance,
            'Swim_Distance': user.stats.swim_distance,
            'Rowing_Distance': user.stats.rowing_distance,
            # Activity times
            'Weightlift_Time': user.stats.weightlift_time,
            'HIIT_Time': user.stats.hiit_time,
            'Stairstepper_Time': user.stats.stairstepper_time,
            # Unique achievements
            'Early_Bird': user.points.early_bird,
            'First_Step': user.points.first_step,
            'Final_Stretch': user.points.final_stretch,
            'Triathlete': user.points.triathlete,
            'Around_the_World': user.points.around_the_world,
            'Club_500': user.points.club_500,
            'Lucky_7s': user.points.lucky_7s,
            'Club_Adventure': user.points.club_adventure,
            # Adventure points
            'Pickleball': user.points.pickleball,
            'Yoga': user.points.yoga,
            'Racquetball': user.points.racquetball,
            'Tennis': user.points.tennis,
            'Soccer': user.points.soccer,
            'Rock_Climb': user.points.rock_climb,
            'Surf': user.points.surf,
            'Kayak': user.points.kayak,
            'Skiing': user.points.skiing,
            'Badminton': user.points.badminton,
            'Golf': user.points.golf,
        }
        data_rows[index] = row
        index += 1
    
    return pd.DataFrame(data_rows)