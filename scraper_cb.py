"""
Small script to scrape central bank meeting dates from www.centralbanknews.info
makes ics file for easy addition to outlook

Kaveh Tehrani
"""

import pandas as pd
import calendar
import os
from bs4 import BeautifulSoup
from requests import get
from ics import Calendar, Event


def scrape_cb_dates():
    url = 'http://www.centralbanknews.info/p/central-bank-calendar_29.html'
    response = get(url)
    print(response.text[:500])

    html_soup = BeautifulSoup(response.text, 'html.parser')
    soup = BeautifulSoup(response.text, "lxml")
    cb_table = soup.find("table")

    abbr_to_num = {name.lower(): num for num, name in enumerate(calendar.month_abbr) if num}
    df_ret = pd.DataFrame(columns=['date', 'fx_code', 'central_bank'])
    for row in cb_table.find_all('td', {'class': 'xl65'}):
        if not row.text:
            continue

        cur_dt = row.text.strip().split('-')
        df_ret = df_ret.append({'date': pd.datetime(2020, abbr_to_num[cur_dt[1].lower()], int(cur_dt[0])),
                                'fx_code': row.next_sibling.text.strip(),
                                'central_bank': row.next_sibling.next_sibling.next_sibling.text.strip()},
                               ignore_index=True)

    return df_ret


if __name__ == '__main__':
    df_cb_dates = scrape_cb_dates()

    str_dir_ics = '.\ics_files'
    os.makedirs(str_dir_ics, exist_ok=True)
    d_sets = dict(zip(df_cb_dates.loc[:, 'fx_code'].unique(), [[x] for x in df_cb_dates.loc[:, 'fx_code'].unique()]))
    d_sets['G10'] = ['EUR', 'GBP', 'USD', 'CAD', 'NOK', 'SEK', 'AUD', 'NZD', 'CHF', 'JPY']
    d_sets['Major_EM'] = ['KRW', 'BRL', 'ZAR', 'TRY']   # that page is missing MXN for some reason
    for idx_cur, cur_set in d_sets.items():
        cal = Calendar()
        for idx, row in df_cb_dates[df_cb_dates['fx_code'].isin(cur_set)].iterrows():
            e = Event()
            e.name = f"{row['fx_code']} CB Meeting"
            e.begin = f"{row['date'].strftime('%Y-%m-%d')}"
            e.make_all_day()
            cal.events.add(e)
            cal.events

        # write ics file
        with open(os.path.join(str_dir_ics, f"{idx_cur}_2020_CB_Dates.ics"), 'w') as f:
            f.write(str(cal))

    print('All done.')
