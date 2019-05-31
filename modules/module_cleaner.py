###############################
# py file does not work, but ipynb does
# File "c:\Users\user\Documents\_user\Projects\Python_Scripts\NTU scrapper\modules\module_cleaner.py", line 65, in <module>
# new_timedf.TIMEFRAME= new_timedf.TIMEFRAME.str[11:-3]
# AttributeError: Can only use .str accessor with string values, which use np.object_ dtype in pandas
###############################

import pandas as pd
import numpy as np
from copy import deepcopy

new_timedict = []


def periods(start, end):

    timedel = end - start
    hour = str(timedel)[7:9]
    mins = str(timedel)[10:12] 

    try: num = int(hour) * 2 + (1 if mins == '30' else 0)
    except: num = 0

    return num

def split_periods(start, end):

    no_periods = periods(start, end) 
    timeframes = [start + pd.to_timedelta('30 min') * i for i in range(no_periods)]
    
    return timeframes


# strip empty txtstr
timetable = pd.read_csv('timetable.csv')
timetable.drop("Unnamed: 0", axis = 1, inplace = True)
timetable.MODULE = timetable.MODULE.str.strip()
timetable.NAME = timetable.NAME.str.strip()

# convert to DT format
timetable['TIMESTART'] = pd.to_datetime(timetable.TIME.str[:4], format = '%H%M')
timetable['TIMEEND'] = pd.to_datetime(timetable.TIME.str[-4:], format = '%H%M')
timetable['PERIODS'] = timetable.apply(lambda x: periods(x.TIMESTART, x.TIMEEND), axis = 1)

# conver to dict
timedict = timetable.to_dict('records')

# split into indv timeframes
for row in timedict:
    start = row['TIMESTART']
    end = row['TIMEEND']
    timeframes = split_periods(start, end)
    
    for timeframe in timeframes:
        new_row = deepcopy(row)
        new_row['TIMEFRAME'] = timeframe
        new_timedict.append(new_row)

# convert to df
new_timedf = pd.DataFrame(new_timedict)

# append back missing data (online)
missing = timetable[timetable.PERIODS == 0].copy()
missing['TIMEFRAME'] = np.nan
missing = missing.reindex(columns = ['DAY','GROUP','INDEX', 'MODULE','NAME','PERIODS','REMARK','TIME','TIMEEND','TIMEFRAME','TIMESTART','TYPE','VENUE'])
new_timedf = new_timedf.append(missing)

# append module, name and type for pivottable
new_timedf['RESULT'] = list(zip(new_timedf.MODULE, new_timedf.NAME, new_timedf.TYPE))

# strip timeframe to only time
new_timedf.TIMEFRAME = new_timedf.TIMEFRAME.str[11:-3]

# add day category for sorting
days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
new_timedf['DAY'] = new_timedf['DAY'].astype("category", categories=days, ordered=True)

# pivot table
pivoted = new_timedf.pivot_table(index = ['DAY','TIMEFRAME'], 
                       values = 'RESULT',
                       columns = 'VENUE', 
                       aggfunc = lambda x: tuple(x))

# save csv
pivoted.to_csv('pivot1.csv')