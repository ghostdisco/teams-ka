import calendar, datetime, json
from app.enums import *
from app.helpers import time_to_datetime
from dataclasses import dataclass
from random import randrange

@dataclass
class Schedule:
    @dataclass
    class Scheduled_Availability:
        available: list[str]
        busy: list[str]
        dnd: list[str]
        away: list[str]
        offline: list[str]

    @dataclass
    class Day:
        def __init__(self, availability, is_workday: bool, use_default: bool, login: str, logout: str) -> None:
            self.use_default = use_default
            self.availability: Schedule.Scheduled_Availability = availability
            self.is_workday = is_workday
            self.login = login
            self.logout = logout

    randomLoginModifierLimit: int
    randomStatusModifierLimit: int
    default: Day
    sun: Day
    mon: Day
    tue: Day
    wed: Day
    thu: Day
    fri: Day
    sat: Day

    def __init__(self) -> None:
        _json = json.load(open('./sched.json'))
        _days = _json['days']
        self.randomLoginModifierLimit = _json['randomLoginModifierLimit']
        self.randomStatusModifierLimit = _json['randomStatusModifierLimit']
        for day in _days.keys():
            j = _days[day]
            s = j['availability']
            self.__dict__[day] = Schedule.Day(
                is_workday=j['is_workday'],
                use_default=j['use_default'],
                login=j['login'],
                logout=j['logout'],
                availability=Schedule.Scheduled_Availability(
                    available=s['available'],
                    busy=s['busy'],
                    dnd=s['dnd'],
                    away=s['away'],
                    offline=s['offline']
                ) 
            )
            if 'default' not in day and self.__dict__[day].use_default:
                self.__dict__[day].login = _days['default']['login']
                self.__dict__[day].logout = _days['default']['logout']
                self.__dict__[day].availability = Schedule.Scheduled_Availability(
                    available=_days['default']['availability']['available'],
                    busy=_days['default']['availability']['busy'],
                    dnd=_days['default']['availability']['dnd'],
                    away=_days['default']['availability']['away'],
                    offline=_days['default']['availability']['offline']
                )

    def _gen_rnd_mod_(self, limit:int, dt:datetime.datetime=None, t:datetime.time=None, subtract:bool=False):

        if not limit:
            return dt if dt else t

        r_mins = randrange(start=0, stop=(limit - 1))
        if subtract: r_mins = r_mins * -1
        r_secs = randrange(start=0, stop=59)
        if subtract: r_secs = r_secs * -1

        if dt:
            dt = dt.__add__(datetime.timedelta(minutes=r_mins))
            dt = dt.__add__(datetime.timedelta(seconds=r_secs))
            return dt
        elif t:
            dt = time_to_datetime(time=t)
            dt = dt.__add__(datetime.timedelta(minutes=r_mins))
            dt = dt.__add__(datetime.timedelta(seconds=r_secs))
            return datetime.time(hour=dt.hour, minute=dt.minute, second=dt.second, microsecond=dt.microsecond)
        else:
            return (r_mins * 60) + r_secs

    def _get_day_identifier_(self, add_days:int=0) -> str:
        identifier = str(calendar.day_name[datetime.date.today().__add__(datetime.timedelta(days=add_days)).weekday()]).lower()[:3]
        return identifier

    def get_today(self) -> Day:
        return self.__dict__[self._get_day_identifier_()]

    def get_future_day(self, add_days:int) -> Day:
        return self.__dict__[self._get_day_identifier_(add_days=add_days)]

    @property
    def desired_availability(self) -> tuple[Availability, datetime.datetime, datetime.datetime]:
        today = self.get_today()
        if not today.is_workday:
            return Availability.OFFLINE
        
        schedule = today.availability
        desired_availability = 'offline'
        now = datetime.datetime.now()
        desired_start = now
        desired_end = now
        for status in schedule.__dict__.keys():
            for entry in schedule.__dict__[status]:
                start = entry.split('-')[0]
                start = time_to_datetime(time=datetime.time(int(start.split(':')[0]), int(start.split(':')[1])), date=now)
                end = entry.split('-')[1]
                end = time_to_datetime(time=datetime.time(int(end.split(':')[0]), int(end.split(':')[1])), date=now)
                if start <= now <= end:
                    desired_availability = status
                    desired_start = start
                    desired_end = end
                    break
                
        return Teams.convert_availability_name_to_enum(value=desired_availability), desired_start, desired_end
    
    @property
    def _holidays_(self) -> list[str]:
        return json.load(open('./holidays.json'))
    
    @property
    def _today_is_holiday_(self) -> bool:
        today = datetime.datetime.today()
        for d in self._holidays_:
            if int(d.split('/')[0]) == today.month:
                if int(d.split('/')[1]) == today.day:
                    return True
        return False

    @property
    def should_be_logged_in(self) -> bool:
        today = self.get_today()
        if not today.is_workday:
            return False
        
        if self._today_is_holiday_:
            return False
        
        now = datetime.datetime.now().time()
        login = datetime.time(int(today.login.split(':')[0]), int(today.login.split(':')[1]))
        logout = datetime.time(int(today.logout.split(':')[0]), int(today.logout.split(':')[1]))

        if self.randomLoginModifierLimit:
            logout = self._gen_rnd_mod_(limit=self.randomLoginModifierLimit, t=logout)
        
        return login <= now <= logout

    def next_login_datetime(self, now:datetime.datetime=None) -> datetime.datetime:

        if not now: now = datetime.datetime.now()
        today_date = now.date()

        # should currently be logged in
        if self.should_be_logged_in:
            return now

        # should login later today
        today = self.get_today() 
        if today.is_workday:
            login = datetime.datetime(year=today_date.year, month=today_date.month, day=today_date.day, hour=int(today.login.split(':')[0]), minute=int(today.login.split(':')[1]))
            if now <= login:
                return login

        # determine next login day
        login_day = 'unk'
        days_from_now = 0
        while days_from_now < 8:
            days_from_now += 1
            day = self.get_future_day(add_days=days_from_now)
            if day.is_workday and day.login:
                login_day = day
                break
        
        # determine seconds until next login
        next_login_datetime = datetime.datetime(year=today_date.year, month=today_date.month, day=today_date.day + days_from_now, hour=int(login_day.login.split(':')[0]), minute=int(login_day.login.split(':')[1]))
        if self.randomLoginModifierLimit:
            next_login_datetime = self._gen_rnd_mod_(limit=self.randomLoginModifierLimit, dt=next_login_datetime)        
        return next_login_datetime
        
    def next_login_in_seconds(self, now:datetime.datetime=None) -> int:
        now = datetime.datetime.now()
        next_login = self.next_login_datetime(now=now)
        seconds = (next_login - now).total_seconds()
        return seconds if seconds >= 0 else 0
   
    

@dataclass
class Teams:
    current_availability: Availability = Availability.UNKNOWN
    
    @property
    def desired_availability(self) -> tuple[Availability, datetime.datetime, datetime.datetime]:
        return self.schedule.desired_availability

    @property
    def should_be_logged_in(self) -> bool:
        return self.schedule.should_be_logged_in

    def next_login_datetime(self, now:datetime.datetime=None) -> datetime.datetime:
        return self.schedule.next_login_datetime(now=now)

    def next_login_in_seconds(self, now:datetime.datetime=None) -> int:
        return self.schedule.next_login_in_seconds(now=now)

    initial_availability: Availability = Availability.UNKNOWN

    last_action: str = None
    profile_name: str = None

    def __init__(self) -> None:
        self.schedule: Schedule = Schedule()

    @staticmethod
    def convert_availability_name_to_enum(value: str) -> Availability:
        try:
            return {
                'available': Availability.AVAILABLE,
                'busy': Availability.BUSY,
                'dnd': Availability.DND,
                'away': Availability.AWAY,
                'offline': Availability.OFFLINE,
                'unknown': Availability.UNKNOWN
            }[value.lower().split(',')[0]]
        except:
            return Availability.UNKNOWN

