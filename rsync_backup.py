__author__ = 'Federico'
"""
Make sure public keys are setup in .ssh directory. At first, it is useful to run ssh from putty for the host
authorization

NOTE: The data is in the server (check via ssh or the web)... It just takes a little while for everything to show
up via the windows share protocol

NOTE: ssh directory is under CWRSYNC_HOME/home - I moved they key and the known_hosts there

TODO: Send some sort of email/notification on failure
"""
import os
import subprocess
import logging
import datetime
import sys

CWRSYNC_HOME = 'D:/Apps/cwRsync_5.5.0_x86_Free'
RSYNC = '{}/bin/rsync.exe'.format(CWRSYNC_HOME)
SSH = '{cwrsync}/bin/ssh.exe -p 1526 -i {cwrsync}/home/Federico/.ssh/id_rsa'.format(cwrsync=CWRSYNC_HOME)

RSYNC_CMD = RSYNC + " -Oavzh --chmod a+rw,Da+x --delete --exclude 'System Volume Information' -e '" + SSH + "' "

DISKSTATION_PATH = 'federico@diskstation:/volume1'
FED_BACKUP_PATH = DISKSTATION_PATH + '/Federico/'
SSD_BACKUP_PATH = FED_BACKUP_PATH + '/GamesSSD/'
PHOTO_BACKUP_PATH = DISKSTATION_PATH + '/photo/'
VIDEO_BACKUP_PATH = DISKSTATION_PATH + '/video/'
MUSIC_BACKUP_PATH = DISKSTATION_PATH + '/music/'

LOG_FILE = '//diskstation/NetBackup/Logs/rsync_backup.' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.log'

# {Remote_dir1: {local_dir_base1, [local_dir1, local_file1],
#                local_dir_base2, [local_dir2, local_file2]}
# CAREFUL! When using the slash after the directory, rsync will delete anything not inside
# the directory you are backing up!
LOCATIONS = {
    FED_BACKUP_PATH: {'/cygdrive/d/': ['Federico', 'Instaladores', 'Apps', 'PortableApps']},
    SSD_BACKUP_PATH: {'/cygdrive/e/': ['']},
    VIDEO_BACKUP_PATH: {'/cygdrive/d/': ['Videos/']},
    MUSIC_BACKUP_PATH: {'/cygdrive/d/': ['Music/']},
    PHOTO_BACKUP_PATH: {'/cygdrive/d/': ['Pictures/']}
}


def main():
    os.environ['HOME'] = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    logger = init_log()
    exit_status = 0

    for target, configs in LOCATIONS.items():
        logger.info('')
        logger.info('Target: %s' % target)

        for base_dir, sources in configs.items():
            logger.info('Base directory: %s' % base_dir)

            for source in sources:
                logger.info('Backing up: %s' % source)
                if run_rsync(base_dir + source, target, logger) != 0:
                    logger.error('Non Zero exit status!')
                    exit_status = 1

    # TrueCrypt does not update timestamps, so use checksums for the container
    logger.info('Backing up: Random (Special case for timestamps)')
    if run_rsync('/cygdrive/d/Random', FED_BACKUP_PATH, logger, '--checksum') != 0:
        logger.error('Non Zero exit status!')
        exit_status = 1

    logger.info('Backup Complete')
    sys.exit(exit_status)


def run_rsync(source, target, logger, rsync_opts=None):
    cmd = RSYNC_CMD.split()
    if rsync_opts is not None:
        cmd.append(rsync_opts)
    cmd.append(source)
    cmd.append(target)

    logger.info('Running {}'.format(' '.join(cmd)))

    rsync = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for line in rsync.stdout:
        logger.info('    ' + line.decode(encoding='UTF-8', errors='ignore').replace('\n', ''))

    return rsync.wait()


def init_log():
    logger = logging.getLogger('basic_logger')
    logger.setLevel(logging.DEBUG)

    handler = logging.FileHandler(LOG_FILE)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(handler)

    logger.info('Logging to STDOUT and %s' % LOG_FILE)
    return logger


if __name__ == '__main__':
    main()