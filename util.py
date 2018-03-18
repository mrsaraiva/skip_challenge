import configparser
import datetime
import os
import platform
import settings as st
import subprocess
import unicodedata


# Debug printing
def d_print(msg, time_in_log=1):
    if st.verbose== 1:
        if time_in_log:
            print(curr_datetime(), end='')
        print(msg)
    if st.log_file:
        with open(st.log_file, 'a') as f:
            if time_in_log:
                f.write(curr_datetime())
            f.write(msg)
            f.write('\n')


def curr_datetime():
    now = datetime.datetime.now()
    time_string = now.strftime('[' + st.log_date_format + '] ')
    return time_string


# Load configuration from file
def load_cfg(cfg_file):
    cfg_file = os.path.abspath(cfg_file)
    cfg = configparser.ConfigParser()
    try:
        with open(cfg_file, 'r') as f:
            cfg.read_file(f)
            d_print('Opened configuration file {0}'.format(cfg_file))
    except (FileNotFoundError, IOError):
        d_print('Could not open configuration file {0}'.format(cfg_file))
        raise ValueError
    return cfg


def remove_diacritics(string):
    string = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode()
    return string


# Save configuration to file
def save_cfg(cfg_file, settings):
    cfg = configparser.ConfigParser()
    if settings.__class__.__name__ == 'defaultdict':
        for section in settings.items():
            cfg[section[0]] = {}
            for k, v in section[1].items():
                cfg[section[0]][k] = str(v)
    else:
        cfg = settings
    try:
        with open(cfg_file, 'w') as f:
            cfg.write(f)
            d_print('Saved settings to {0}'.format(cfg_file))
    except IOError:
        d_print('Could not save settings to {0}'.format(cfg_file))


# Open a directory with the shell default handler
def shell_open_directory(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])