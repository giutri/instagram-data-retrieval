#!/usr/bin/env python
# coding: utf-8

from igramscraper.instagram import Instagram
import time
import random
import pandas as pd
import numpy as np
import os
import requests
import json
import sys
from tqdm import tqdm, tqdm


# ## SCRAPER


def getUserFollowers(instagram, username, count=None, delayed_time_min=18.0, delayed_time_max=20.0):
    followings = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }

    try:
        account = instagram.get_account(username)

        if account.is_private == 1:
            print("account is private. Skipping...")
            return [], 1
        else:
            try:
                following = instagram.get_followers(
                    account.identifier, 
                    count= count, 
                    page_size=48, 
                    delayed=True,
                    delayed_time_min=delayed_time_min, #min inter-request time
                    delayed_time_max=delayed_time_max, #max inter-request time
                    rate_limit_sleep_min=3600.0, #1h min wait
                    rate_limit_sleep_max=2*3600.0, #2h max wait
                )
                
                for following_user in following['accounts']:
                    followings.append(account_info_to_dict(following_user))
                    
                return pd.DataFrame(followings), 0

            except Exception as e:
                if '429' in str(e)[:100]:
                    print('Error 429: Rate Limit Reached.')
                return [], 1

    except Exception as e:
        print("account doesn't exist or some error occurred.." + str(e))
        return [], 1


def getUserFollows(instagram, username, count=None, delayed_time_min=18.0, delayed_time_max=20.0):
    followings = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        }

    try:
        account = instagram.get_account(username)

        if account.is_private == 1:
            print("account privated. Skipping...")
            return [], 1
        elif account.follows_count == 0:
            print('follows no one. Skipping...')
            return [], 1
        else:
            try:
                following = instagram.get_following(
                    account.identifier, 
                    count= account.follows_count, 
                    page_size=min(account.follows_count,48), 
                    delayed=True,
                    delayed_time_min=delayed_time_min, #min inter-request time
                    delayed_time_max=delayed_time_max, #max inter-request time
                    rate_limit_sleep_min=3600.0, #1h min wait
                    rate_limit_sleep_max=2*3600.0, #2h max wait
                )
                
                for following_user in following['accounts']:
                    followings.append(account_info_to_dict(following_user))
                    
                return pd.DataFrame(followings), 0

            except Exception as e:
                if '429' in str(e)[:100]:
                    print('Error 429: Rate Limit Reached.')
                return [], 1


    except Exception as e:
        print("account doesn't exist or some error occurred.." + str(e))
        return [], 1



def get_n_recent_followers(instagram, influencers, count, follows=False, delayed_time_min=18.0, delayed_time_max=20.0):
    
    try:
        os.mkdir('INFLUENCER')
    except FileExistsError:
        pass
    
    try:
        os.mkdir('INFLUENCER/FOLLOWS')
        os.mkdir('INFLUENCER/FOLLOWERS')

    except FileExistsError:
        pass
    
    if follows:
        print('Get FOLLOWS')
    else:
        print('Get FOLLOWERS')
        
    for influencer in tqdm(influencers):
        try:
            account = instagram.get_account(influencer)
            tqdm.write(account)
        
            if follows:
                tqdm.write('get follows...')
                F, error = getUserFollows(instagram, influencer, delayed_time_min=delayed_time_min, delayed_time_max=delayed_time_max)
                if not error:
                    tqdm.write('save to csv...')
                    F.to_csv('./INFLUENCER/FOLLOWS/'+influencer+'_follows.csv')
                    tqdm.write('csv saved')
            else:
                tqdm.write('get followers...')
                F, error = getUserFollowers(instagram, influencer, count, delayed_time_min=delayed_time_min, delayed_time_max=delayed_time_max)
                if not error:
                    tqdm.write('save to csv...')
                    F.to_csv('./INFLUENCER/FOLLOWERS/'+influencer+'_followers_'+str(count)+'.csv')
                    tqdm.write('csv saved')

        except Exception as e:
            tqdm.write('Cannot Retrive Influencer Data.')

            if '429' in str(e)[:100]:
                    tqdm.write('Error 429: Rate Limit Reached.')



def get_following_counts(F, instagram, delayed=True,  delayed_time_min=18.0, delayed_time_max=20.0):
    
    followers_info = []
    
    for user_id in tqdm(list(F['id'].values)):
        
        if delayed:
            d_time = random.uniform(delayed_time_min, delayed_time_max)
            time.sleep(d_time)
        try:
            account = instagram.get_account_by_id(user_id)

            if account.is_private == 1:
                pass
                #print("account privated. Skipping...")
            else:
                followers_info.append(account_info_to_dict(account))
                
        except Exception as e:
            if '429' in str(e)[:100]:
                tqdm.write('Error 429: Rate Limit Reached.')
        
    return pd.DataFrame(followers_info)


# ## API

def account_info_to_dict(account):
    D = dict()
    D['id'] = account.identifier
    D['username'] = account.username
    D['followers_count'] = account.followed_by_count
    D['follows_count'] = account.follows_count
    D['is_business_account'] = account.is_business_account
    D['is_verified'] = account.is_verified
    D['business_email'] = account.business_email
    D['business_category'] = account.business_category_name
    D['joined_recently'] = account.is_joined_recently
    D['biography'] = account.biography
    D['website'] = account.external_url
    return D



def getAccountInfo( params ) :
    """ Get info on a users account

    API Endpoint:
        https://graph.facebook.com/{graph-api-version}/{ig-user-id}?fields=business_discovery.username({ig-username}){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count}&access_token={access-token}

    Returns:
        object: data from the endpoint

    """

    endpointParams = dict() # parameter to send to the endpoint
    endpointParams['fields'] = 'business_discovery.username(' + params['ig_username'] + '){username,website,name,ig_id,id,profile_picture_url,biography,follows_count,followers_count,media_count}' # string of fields to get back with the request for the account
    endpointParams['access_token'] = params['access_token'] # access token

    url = params['endpoint_base'] + params['instagram_account_id'] # endpoint url

    return makeApiCall( url, endpointParams, params['debug'] ) # make the api call



def getCreds(username) :
    """ 
    # REQUIRES facebook for business account.

    Args:
        Get creds required for use in the applications

    Returns:
        dictonary: credentials needed globally

    """

    creds = dict() # dictionary to hold everything
    creds['access_token'] = 'LONG_ACCESS_TOKEN'
    creds['client_id'] = 'CLIENT_ID' # client id from facebook app IG Graph API Test
    creds['client_secret'] = 'CLIENT_SECRET' # client secret from facebook app
    creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
    creds['graph_version'] = 'v6.0' # version of the api we are hitting
    creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] + '/' # base endpoint with domain and version
    creds['debug'] = 'no' # debug mode for api call
    creds['page_id'] = 'PAGE_ID' # users page id
    creds['instagram_account_id'] = 'ACCOUNT_ID' # users instagram account id
    creds['ig_username'] = username # ig username

    return creds

def makeApiCall( url, endpointParams, debug = 'no' ) :
    """ Request data from endpoint with params

    Args:
        url: string of the url endpoint to make request from
        endpointParams: dictionary keyed by the names of the url parameters


    Returns:
        object: data from the endpoint

    """

    data = requests.get( url, endpointParams ) # make get request

    response = dict() # hold response info
    response['url'] = url # url we are hitting
    response['endpoint_params'] = endpointParams #parameters for the endpoint
    response['endpoint_params_pretty'] = json.dumps( endpointParams, indent = 4 ) # pretty print for cli
    response['json_data'] = json.loads( data.content ) # response data from the api
    response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

    if ( 'yes' == debug ) : # display out response info
        displayApiCallData( response ) # display response

    return response # get and return content

def displayApiCallData( response ) :
    """ Print out to cli response from api call """

    print("\nURL: ")# title
    print(response['url'])# display url hit
    print("\nEndpoint Params: ")# title
    print(response['endpoint_params_pretty']) # display params passed to the endpoint
    print("\nResponse: ") # title
    print(response['json_data_pretty']) # make look pretty for cli


def getUserFollowCounts_API(F, delayed=True,  delayed_time_min=18.0, delayed_time_max=20.0):
    
    L = []
    #display(F)
    for user in tqdm(list(F['username'].values)):
        
        if delayed:
            d_time = random.uniform(delayed_time_min, delayed_time_max)
            time.sleep(d_time)
        
        D = dict()
        D['username'] = None
        D['website'] = None
        D['media_count'] = None
        D['followers_count'] = None
        D['follows_count'] = None
        D['biography'] = None
        
        params = getCreds(user) # get creds
        params['debug'] = 'no' # set debug
        response = getAccountInfo( params ) # hit the api for some data!

        if 'error' in list(response['json_data'].keys()):
            tqdm.write(response['json_data']['error']['message'])
            #print('error, invalid user')
        else:

            try:
                #print('username:')
                #print(response['json_data']['business_discovery']['username'])
                D['username'] = response['json_data']['business_discovery']['username']
            except:
                pass
            try:
                #print('website:')
                #print(response['json_data']['business_discovery']['website'])
                D['website'] = response['json_data']['business_discovery']['website']
            except:
                pass
            try:
                #print('media count:')
                #print(response['json_data']['business_discovery']['media_count'])
                D['media_count'] = response['json_data']['business_discovery']['media_count']
            except:
                pass
            try:
                #print('followers count:')
                #print(response['json_data']['business_discovery']['followers_count'])
                D['followers_count'] = response['json_data']['business_discovery']['followers_count']
            except:
                pass
            try:
                #print(response['json_data']['business_discovery']['follows_count'])
                D['follows_count'] = response['json_data']['business_discovery']['follows_count']
            except:
                pass
            try:
                #print(response['json_data']['business_discovery']['biography'])
                D['biography'] = response['json_data']['business_discovery']['biography']
            except:
                pass     
            
            #print(D['username'], D['followers_count'], D['follows_count'] )
            L.append(D)
            
    return pd.DataFrame(L).sort_values(by=['followers_count'], ascending=False)
                    


# ## GENERAL


def read_follow_dataframes(TYPE=None):
    L = []
    L_names = []
    for item in os.listdir('./INFLUENCER/'+TYPE):
        L.append(pd.read_csv('./INFLUENCER/'+TYPE+'/'+item, index_col=0))
        L_names.append(str(item).split('_')[0])
        
    print('total user count:', np.array([len(x) for x in L]).sum())
    return L, L_names


def sort_follow_dataframes(TYPE=None):
    for item in [f for f in os.listdir('./INFLUENCER_POPULATED/'+TYPE) if not f.startswith('.')]:

        df =pd.read_excel('./INFLUENCER_POPULATED/'+TYPE+'/'+item, index_col=0)
        df_ = df.sort_values(by=['followers_count'], ascending=False)
        df_.to_excel('./INFLUENCER_POPULATED/'+TYPE+'/'+str(item))
        
        del df, df_



def populate_follower_info(Follower_DF, influencer_names, instagram=None, follows=False, use_API = None, delayed_time_min=18.0, delayed_time_max=20.0):
    
    try:
        os.mkdir('INFLUENCER_POPULATED')
    except FileExistsError:
        pass
    
    try:
        os.mkdir('INFLUENCER_POPULATED/FOLLOWS')
        os.mkdir('INFLUENCER_POPULATED/FOLLOWERS')

    except FileExistsError:
        pass
    
    if follows:
        print('Get FOLLOWS')
    else:
        print('Get FOLLOWERS')
        
    for F, name in zip(Follower_DF, influencer_names):
        print('influencer:', name,'user count:', len(F))
        
        if use_API:
            F_final = getUserFollowCounts_API(F, delayed_time_min=delayed_time_min, delayed_time_max=delayed_time_max)
        else:
            F_final = get_following_counts(F, instagram, delayed_time_min=delayed_time_min, delayed_time_max=delayed_time_max)
            
        if follows:
            if use_API:
                F_final.to_excel('INFLUENCER_POPULATED/FOLLOWS/'+name+'_API.xlsx')
            else:
                F_final.to_excel('INFLUENCER_POPULATED/FOLLOWS/'+name+'.xlsx')

        else:
            if use_API:
                F_final.to_excel('INFLUENCER_POPULATED/FOLLOWERS/'+name+'_'+str(len(F))+'_API.xlsx')
            else:
                F_final.to_excel('INFLUENCER_POPULATED/FOLLOWERS/'+name+'_'+str(len(F))+'.xlsx')




