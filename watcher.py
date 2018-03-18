# Github repo watcher - Skip the Dishes DevOps challenge
# You need to setup ~/aws/config, the contents are available on the Vanhack project description
# You also need ~/aws/credentials (details available on the project description as well)
# The API key available on the last commit was revoked, to avoid people stopping or modifying the test application,
# which was the only the permissions given to that credential


# Missing stuff to implement:
# - Daemonize the watcher
# - Check failures during the deployment phase
# - Send alerts when the tests or any other part of the continuous deployment fails
# - Make the code prettier

from git import Repo
from zipfile import ZipFile
import boto3
import feedparser
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
#import util as ut


# Git repo stuff
repo_url = 'https://github.com/mrsaraiva/test_repo/'
feed_path = 'commits/master.atom'
feed_url = repo_url + feed_path
current_etag = ''
previous_etag = ''

# Local directories and files
etag_file = 'etag.txt'
staging_repo_dir = os.path.abspath('./test_repo')
test_filename = 'test.py'
test_file_path = os.path.join(staging_repo_dir, test_filename)
zip_filename = 'application.zip'
zip_file_path = os.path.join(staging_repo_dir, zip_filename)

# S3 stuff
ebs_appname = 'skip_challenge'
ebs_environment_id = 'e-hcdz3nqp3p'
s3_bucket = 'elasticbeanstalk-sa-east-1-878068589872'
s3_file_path = s3_bucket + '/' + zip_filename

# Misc
alert_msg = ''
python3_bin = '/usr/local/bin/python3'

# Load file with the current etag, or create one if it doesn't exist
try:
    with open(etag_file, 'r') as f:
        current_etag = f.read()
        previous_etag = current_etag
except FileNotFoundError:
    open(etag_file, 'w').close()

# Check Github repo for changes
def check_repo(delay):
    global current_etag
    while True:
        parser = feedparser.parse(feed_url)
        feed_etag = parser['etag'].strip('"')
        if current_etag != feed_etag:
            print('repo was modified')
            current_etag = feed_etag
            with open(etag_file, 'w') as f:
                f.write(feed_etag.strip('"'))
            clone_repo()
        else:
            print('repo not modified')
        time.sleep(delay)


def clone_repo():
    print('Cloning repo to tmp dir')
    if os.path.exists(staging_repo_dir):
        shutil.rmtree(staging_repo_dir, ignore_errors=True)
    Repo.clone_from(repo_url, staging_repo_dir)
    run_tests()


def create_package():
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
    try:
        dirs_to_exclude = ['.git', 'tmp']
        files_to_exclude = ['.DS_Store', 'README.md', 'LICENSE']
        files_to_write = {}
        for root, dirs, files in os.walk(staging_repo_dir):
            for d in dirs:
                if d in dirs_to_exclude:
                    dirs.remove(d)
                else:
                    arcname = d
                    d = os.path.join(staging_repo_dir, d)
                    files_to_write[d] = arcname
            for file in files:
                if file not in files_to_exclude:
                    arcname = file
                    file = os.path.join(staging_repo_dir, file)
                    files_to_write[file] = arcname
        with ZipFile(zip_file_path, 'w') as zip:
            for files, archive_name in files_to_write.items():
                zip.write(files, arcname=archive_name)
        print('Package created!')
    except OSError as e:
        error_msg = 'Error while creating the zip package'
        process_failed()


def deploy():
    create_package()
    ebs_client = boto3.client('elasticbeanstalk')
    s3_client = boto3.resource('s3')
    data = open(zip_file_path, 'rb')
    s3_client.Bucket(s3_bucket).put_object(Key=zip_filename, Body=data)

    # Create a new version on EBS
    response = ebs_client.create_application_version(
        ApplicationName=ebs_appname,
        VersionLabel=current_etag,
        Description='Auto-deployed from CI',
        SourceBundle={
            'S3Bucket': s3_bucket,
            'S3Key': zip_filename
        },
        AutoCreateApplication=True,
        Process=False
    )

    # Update environment to use the uploaded version
    response = ebs_client.update_environment(
        ApplicationName=ebs_appname,
        VersionLabel=current_etag,
        EnvironmentId=ebs_environment_id
    )
    print('Application deployed to production environment on EBS!')


def process_failed():
    global alert_msg, current_etag
    current_etag = previous_etag
    send_alert()


def rollback():
    pass

def run_tests():
    test_exec = subprocess.run([python3_bin, test_file_path], stdout=subprocess.PIPE)
    test_exec_output = test_exec.stdout.decode("utf-8")
    if 'ERROR' in test_exec_output:
        send_alert()
    else:
        deploy()


def send_alert():
    pass


def signal_handler(signum, frame):
    print('Received SIGTERM, bye!')
    sys.exit(1)


signal.signal(signal.SIGTERM, signal_handler)
t = threading.Timer(3, check_repo, args=[15])
t.start()
