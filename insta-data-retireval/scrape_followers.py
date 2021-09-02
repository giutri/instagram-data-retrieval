#!/usr/bin/env python
# coding: utf-8

from igramscraper.instagram import Instagram
import sys
from scraper_lib import *

# ## instagram login
acc_user = sys.argv[1]
acc_pass = sys.argv[2]
count = sys.argv[3]

print('user:', acc_user, acc_pass)
print('count:', count)

acc_user = 'USERNAME'
acc_pass = 'PASSWORD'

instagram = Instagram()

# authentication supported
instagram.with_credentials(acc_user, acc_pass)
instagram.login(force=False,two_step_verificator=True)


# ## Scrape Influencer for Followers

# preset list of user accounts to retain publically obtainable list of followers from
iDATA = pd.read_excel('filtered_influencers.xlsx')
influencers = list(iDATA['Username'].values)

print('begin influencer scrape')
get_n_recent_followers(instagram, influencers, count, follows=True)
