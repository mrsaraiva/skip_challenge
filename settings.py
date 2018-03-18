# settings.py
from collections import defaultdict
import appdirs
import globals as glb
import os
import util as ut

data_dir = appdirs.user_data_dir(glb.APPNAME, glb.APPAUTHOR, roaming=True)
main_cfgfile = os.path.join(data_dir, 'watcher.cfg')
main_cfg = defaultdict(lambda: dict())
log_date_format = '%Y-%m-%d %H:%M:%S'
log_file = os.path.join(data_dir, 'watcher.log')
verbose = 1
mode = 'standalone'


def init_settings():
    global log_date_format
    global log_file
    global verbose
    global mode
    global profile_dir
    global sheet_dir
    global output_dir
    log_date_format = main_cfg['log']['date_format']
    log_file = os.path.join(data_dir, main_cfg['log']['log_file'])
    verbose = main_cfg['log']['verbose']
    mode = main_cfg['main']['mode']
    profile_dir = os.path.join(data_dir, main_cfg['main']['profile_dir'])
    sheet_dir = os.path.join(data_dir, main_cfg['main']['sheet_dir'])
    output_dir = os.path.join(data_dir, main_cfg['main']['output_dir'])


def generate_default_main_settings():
    ut.d_print('Using default settings')
    main_cfg['log']['date_format'] = '%%Y-%%m-%%d %%H:%%M:%%S'
    main_cfg['log']['log_file'] = 'watcher.log'
    main_cfg['log']['verbose'] = 1
    main_cfg['main']['mode'] = 'standalone'
    ut.save_cfg(main_cfgfile, main_cfg)
    main_cfg['log']['date_format'] = '%Y-%m-%d %H:%M:%S'


def load_main_settings():
    try:
        print('hi')
        cfg = ut.load_cfg(main_cfgfile)
        main_cfg['log']['date_format'] = cfg['log']['date_format']
        main_cfg['log']['log_file'] = cfg['log']['log_file']
        main_cfg['log']['verbose'] = int(cfg['log']['verbose'])
        main_cfg['main']['mode'] = cfg['main']['mode']
    except ValueError:
        print('ho')
        generate_default_main_settings()
    finally:
        init_settings()


def init():
    load_main_settings()


init()