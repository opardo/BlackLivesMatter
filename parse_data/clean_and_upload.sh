#!/bin/bash
for i in {1..10}
do
   gsutil cp gs://fergusontweets2014_json/$i.json $i.json
   sed -e '1s/^/[/' -e 's/$/,/' -e '$s/,$/]/' $i.json > tw$i.json
   python parse_json.py --int_file $i
   #bq load --source_format CSV  --max_bad_records 500 --autodetect  tweets.tweets_$i  tw$i.csv
   rm $i.json
   rm tw$i.json
done

