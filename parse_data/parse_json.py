import argparse
import csv
import json
import pandas as pd

COLUMNS = ['contributors', 'coordinates', 'created_at', 'display_text_range',
       'favorite_count', 'favorited', 'full_text', 'geo', 'id', 'id_str',
       'in_reply_to_screen_name', 'in_reply_to_status_id',
       'in_reply_to_status_id_str', 'in_reply_to_user_id',
       'in_reply_to_user_id_str', 'is_quote_status', 'lang', 'place',
       'possibly_sensitive', 'retweet_count', 'retweeted', 'source',
       'truncated', 'retweeted_status', 'extended_entities',
       'quoted_status_id', 'quoted_status_id_str', 'quoted_status_permalink',
       'quoted_status', 'hashtags', 'symbols', 'urls', 'user_mentions',
       'media', 'user_id_mentions', 'user_screen_name_mentions',
       'user_contributors_enabled', 'user_created_at', 'user_default_profile',
       'user_default_profile_image', 'user_description', 'user_entities',
       'user_favourites_count', 'user_follow_request_sent',
       'user_followers_count', 'user_following', 'user_friends_count',
       'user_geo_enabled', 'user_has_extended_profile', 'user_id',
       'user_id_str', 'user_is_translation_enabled', 'user_is_translator',
       'user_lang', 'user_listed_count', 'user_location', 'user_name',
       'user_notifications', 'user_profile_background_color',
       'user_profile_background_image_url',
       'user_profile_background_image_url_https',
       'user_profile_background_tile', 'user_profile_image_url',
       'user_profile_image_url_https', 'user_profile_link_color',
       'user_profile_sidebar_border_color', 'user_profile_sidebar_fill_color',
       'user_profile_text_color', 'user_profile_use_background_image',
       'user_protected', 'user_screen_name', 'user_statuses_count',
       'user_time_zone', 'user_translator_type', 'user_url', 'user_utc_offset',
       'user_verified', 'user_profile_banner_url']

def list_hashtags(row):
    hashtags = []
    for i in row:
        hashtags.append(i['text'])
    return json.dumps(hashtags)

def list_urls(row):
    urls = []
    for i in row:
        urls.append(i['url'])
    return json.dumps(urls)

def list_user_id_mentions(row):
    ids = []
    for i in row:
        ids.append(i['id'])
    return json.dumps(ids)

def list_user_screen_name_mentions(row):
    screen_names = []
    for i in row:
        screen_names.append(i['screen_name'])
    return json.dumps(screen_names)

def list_url_media(row):
    urls = []
    try:
        for i in row:
            urls.append(i['expanded_url'])
        return json.dumps(urls)
    except:
        return json.dumps(urls)

def list_symbols(row):
    texts = []
    for i in row:
        texts.append(i['text'])
    return json.dumps(texts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', help='Number/ name of json file')
    args = parser.parse_args()
    file_name = args.file_name
    # Read File
    with open('{}.json'.format(file_name), 'r') as json_file:
        data = json.load(json_file)

    # Convert to pandas dataframe
    df_json = pd.DataFrame(data)

    # Convert entities column to a new dataframe
    df_entities = df_json['entities'].apply(pd.Series).copy()
    # Clean columns of entities
    df_entities['hashtags'] = df_entities['hashtags'].map(list_hashtags)
    df_entities['urls'] = df_entities['urls'].map(list_urls)
    df_entities['user_id_mentions'] = df_entities['user_mentions'].map(list_user_id_mentions)
    df_entities['user_screen_name_mentions'] = df_entities['user_mentions'].map(list_user_screen_name_mentions)
    if 'media' in df_entities.columns:
        df_entities['media'] = df_entities['media'].map(list_url_media)
    else:
        df_entities['media'] = None
    df_entities['symbols'] = df_entities['symbols'].map(list_symbols)

    # Convert user column to a new data frame
    df_user = df_json['user'].apply(pd.Series).copy()
    df_user.columns = ['user_{}'.format(x) for x in df_user.columns]

    # Drop entities and user columns
    df_json = df_json.drop(['entities', 'user'], axis=1)

    # Clean other columns
    if 'extended_entities' in df_json.columns:
        df_json['extended_entities'] = df_json['extended_entities'].apply(lambda x: json.dumps(x) if type(x) == dict else json.dumps(dict()))
    else:
        df_json['extended_entities'] = json.dumps(dict())

    if 'quoted_status' in df_json.columns:
        df_json['quoted_status'] = df_json['quoted_status'].apply(lambda x: json.dumps(x) if type(x) == dict else json.dumps(dict()))
    else:
        df_json['quoted_status'] = json.dumps(dict())

    if 'quoted_status_permalink' in df_json.columns:
        df_json['quoted_status_permalink'] = df_json['quoted_status_permalink'].apply(lambda x: json.dumps(x) if type(x) == dict else json.dumps(dict()))
    else:
        df_json['quoted_status_permalink'] = json.dumps(dict())

    # Concatentate the 3 dataframes
    df_json_all = pd.concat([df_json, df_entities, df_user], axis=1)
    # Add missing columns if needed
    missing = [x for x in COLUMNS if x not in df_json_all.columns]
    for i in missing:
        df_json_all[i] = None

    # Save csv file
    df_json_all[COLUMNS].to_csv('{}.csv'.format(file_name), index=False,  header=True,
            quoting=csv.QUOTE_NONNUMERIC)
