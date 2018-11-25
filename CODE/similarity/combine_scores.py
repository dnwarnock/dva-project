import os
import sys
import shutil
import pandas as pd
from sklearn import preprocessing
from subprocess import check_call


def sync_files(metric_type):
    if not os.path.isdir(metric_type):
        os.mkdir(metric_type)

    s3_path = "s3://dva-gatech-atx/sim_results/{}".format(metric_type)
    loc_path = "./{}/".format(metric_type)
    cmd = "aws s3 sync {s3_path} {loc_path}".format(
            s3_path=s3_path,
            loc_path=loc_path
        )

    print("executing {}".format(cmd))
    check_call(cmd, shell=True)

def make_df(metric_type):
    dfs = []
    for root, dirs, files in os.walk("{}/".format(metric_type)):
        for file in files:
            if file[-4:] != '.csv':
                continue
            print("processing file {}/{}".format(metric_type, file))
            df = pd.read_csv("{}/{}".format(metric_type, file))
            if metric_type == 'lsh':
                df = df[df['sim_rank'] <= 20]
            dfs.append(df)

    df = pd.concat(dfs)

    if metric_type == 'lsh':
        del df['sim_metric']
    else:
        del df['metric']

    # convert distance to similarity & normalize
    df['sim_score'] = df['sim_score'].max() - df['sim_score']
    scaler = preprocessing.MinMaxScaler()
    df['sim_score'] = scaler.fit_transform(pd.DataFrame(df['sim_score'], columns=['sim_score']))

    file_name = "{}_similarities.csv".format(metric_type)
    s3_dest = "s3://dva-gatech-atx/prepared_data/"
    df.to_csv(file_name, index=False)

    print("uploading {}".format(file_name))
    check_call("aws s3 cp {file_name} {s3_path}".format(
            file_name=file_name,
            s3_path=s3_dest
        ),
        shell=True
    )

def cleanup(metric_type):
    print("deleting local files for {}".format(metric_type))
    shutil.rmtree('{}/'.format(metric_type))

def main(metric_types):
    for metric_type in metric_types:
        sync_files(metric_type)
        make_df(metric_type)
        cleanup(metric_type)

if __name__ == '__main__':
    if sys.argv[1] == 'euclid':
        main(['euclid'])
    elif sys.argv[1] == 'manhattan':
        main(['manhattan'])
    elif sys.argv[1] == 'lsh':
        main(['lsh'])
    elif sys.argv[1] == 'all':
        main(['euclid', 'manhattan', 'lsh'])
    else:
        raise Exception("Expected argument value to be `euclid`, `manhattan`, `lsh` or `all`. Got {}".format(sys.argv[1]))
