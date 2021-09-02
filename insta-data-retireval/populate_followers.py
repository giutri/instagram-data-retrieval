#!/usr/bin/env python
# coding: utf-8

from igramscraper.instagram import Instagram
import sys
from scraper_lib import *

# ## instagram login
acc_user = sys.argv[1]
acc_pass = sys.argv[2]
start_from = int(sys.argv[3])
use_API = sys.argv[4] == 'True'
min_delay = int(sys.argv[5])
max_delay = int(sys.argv[6])

print("Populate User Data Script")


print('scraper account user:', acc_user, 'pass:', acc_pass)
print('start from influencer list number:', start_from)
print('min request delay:', min_delay, 'max request delay', max_delay)

instagram = Instagram()

# authentication supported
instagram.with_credentials(acc_user, acc_pass)
instagram.login(force=False,two_step_verificator=True)

if use_API:
    print('using API')
else:
    print('using Scraper')
Follower_DF, influencer_names = read_follow_dataframes(TYPE='FOLLOWS')
populate_follower_info(Follower_DF[start_from:], influencer_names[start_from:], instagram=instagram, follows=True, use_API=use_API, delayed_time_min=min_delay, delayed_time_max=max_delay)
sort_follow_dataframes(TYPE='FOLLOWS')

