import calendar
from datetime import datetime, time, timedelta
from sqlalchemy.orm import sessionmaker
from models import Weeks, db_connect
import pytz
import sys

def next_weekday(start_date, weekday):
    days_ahead = weekday - start_date.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return start_date + timedelta(days_ahead)

def get_weeks(start_date, end_date):
    ONE_DAY, ONE_WEEK = timedelta(days=1), timedelta(days=7)
    current_week_start = calendar.Calendar(3).monthdatescalendar(start_date.year, start_date.month)[0][0]

    week_num = 1
    while True:
        if current_week_start + ONE_WEEK <= start_date:
            current_week_start += ONE_WEEK
            continue
        if current_week_start > end_date:
            break
        yield [week_num,
               current_week_start.strftime('%Y-%m-%d'),
               (current_week_start + ONE_WEEK - ONE_DAY).strftime('%Y-%m-%d'),
               datetime.combine(current_week_start + (ONE_DAY*3), time(hour=12, minute=30)),
               datetime.combine(current_week_start - (ONE_DAY*2), time(hour=0))]

        current_week_start += ONE_WEEK
        week_num += 1

def season_weeks():
    ONE_DAY, ONE_WEEK = timedelta(days=1), timedelta(days=7)
    utc, east = pytz.utc, pytz.timezone('US/Eastern')
    current_season = (datetime.now().year - 1) if datetime.now().month < 6 else datetime.now().year

    if len(sys.argv) > 1:
        current_season = int(sys.argv[-1])

    print('CURRENT SEASON: ', current_season)
    
    first_monday_in_sept = next_weekday(datetime(current_season, 9, 1).date(), 0)  # 0=Monday, 1=Tuesday, 2=Wednesday...

    regular_start = next_weekday(first_monday_in_sept, 3)  # 3=Thursday
    preseason_start = regular_start - timedelta(weeks=4)
    playoff_start = regular_start + timedelta(weeks=17)

    regular_end = playoff_start - ONE_DAY
    preseason_end = regular_start - ONE_DAY
    playoff_end = playoff_start + timedelta(weeks=5) - ONE_DAY

    weeks = []
    season_parts = ['regular', 'preseason', 'playoffs']
    season_parts_dates = [[regular_start, regular_end], [preseason_start, preseason_end], [playoff_start, playoff_end]]
    for i, season_part in enumerate(season_parts_dates):
        for week in get_weeks(season_part[0], season_part[1]):
            padded_week_num = '0'+str(week[0]) if len(str(week[0])) < 2 else str(week[0])
            week_row = {
                'season': current_season,
                'season_part': season_parts[i],
                'week': week[0],
                'start_date': week[1],
                'end_date': week[2],
                # 'lines_close_time': east.localize(week[3]).astimezone(utc).replace(tzinfo=None).isoformat(),
                # 'lines_open_time': east.localize(week[4]).astimezone(utc).replace(tzinfo=None).isoformat(),
                'week_key': str(current_season) + season_parts[i][:3].upper() + padded_week_num
            }
            yield week_row


def write_weeks():
    """Save weeks in the database.
    """
    engine = db_connect()
    Session = sessionmaker(bind=engine)

    for week in season_weeks():
        session = Session()
        # check if item with this key exists in table
        week_exists = session.query(Weeks).filter_by(week_key=week['week_key']).first()
        if not week_exists:
            week_row = Weeks(**week)
            week_row.save_time = datetime.utcnow().isoformat()
            try:
                session.add(week_row)
                session.commit()
                print('Writing', week_row.season_part, 'week', week_row.week)
            except:
                session.rollback()
                raise
        session.close()


write_weeks()