import os
import pandas as pd
from subprocess import check_call

zips = [78730, 78731, 78735, 78702, 78701, 78703, 78704, 78750, 78759, 78758, 78757, 78753, 78752, 78727, 78723, 78721, 78742, 78745, 78749, 78741, 78729, 78756, 78722]

base_df = pd.read_csv('data/CENTRAL_ATX_SUBSET.csv')

for atx_zip in zips:
    filter_df = base_df[base_df['situs_zip'] == str(atx_zip)]
    file_name = str(atx_zip) + '.csv'
    filter_df.to_csv(file_name, index=False)
    check_call("aws s3 cp {file} s3://dva-gatech-atx/zillow/{zip}/input/".format(
        file=file_name,
        zip=atx_zip
    ),
        shell=True
    )
