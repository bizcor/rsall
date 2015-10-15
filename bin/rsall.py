#!/usr/bin/python

import os
import random
import socket
import sys
sys.path.append(os.environ['HOME'] + '/Dropbox/sys/python/lib/mylib')
from system_command import system_command

USER = os.environ.get('LOGNAME')
HOST = socket.gethostname().split('.')[0]
volume_names = ['delenn', 'gkar', 'londo', 'sheridan']

backup_configuration = {
   'rsync_options': ['--archive', '--delete', '--exclude-from',
                     '<<<EXCLUDE_FILE>>>', '--progress', '<<<SOURCE>>>/',
                     '<<<DESTINATION>>>/'],
   'exclude_file_directory': '/Users/{}/etc'.format(USER),
   'sources': [
       {
           'source': '/Users/{}'.format(USER),
           'destinations': ["/{}/spool/rsync/{}/Users/{}".format(d, HOST, USER)
                            for d in volume_names],
           'exclude_file': 'rsync.exclude.{}-Users-{}'.format(HOST, USER),
       },
       {
           'source': '/usr/local/perforce',
           'destinations': ["/{}/spool/rsync/{}/usr/local/perforce".
                            format(d, HOST) for d in volume_names],
           'exclude_file': 'rsync.exclude.{}-usr-local-perforce'.format(HOST),
       },
   ]
}


def get_tickle_file_basename():
    '''return a string which will be used as the basename of the "tickle" file
    '''
    low = 1000
    high = 2000
    return ".tickle-{}-{}".format(str(random.randint(low, high)),
                                  str(random.randint(low, high)))


def wake_up_external_drives(volume_names):
    '''wake up external drives so that we don't get i/o errors rsync'ing
       to them.  for each volume, write a random file to it and fsync() the
       file.
    '''
    number_of_child_processes = 0

    for volume_name in volume_names:
        VOLUME_PATH = '/Volumes/{}'.format(volume_name)

        newpid = os.fork()

        if newpid == 0:
            # child process
            print "waking {}...".format(volume_name)
            tickle_file_path = "{}/{}".format(VOLUME_PATH,
                                              get_tickle_file_basename())
            with open(tickle_file_path, 'w') as tickle_file:
                tickle_file.write(':-D')
                tickle_file.flush()
                os.fsync(tickle_file)
            os.remove(tickle_file_path)

            print "...{} is awake".format(volume_name)
            exit(0)
        else:
            # parent process.  increment count of children to wait for.
            number_of_child_processes += 1

    # wait for all drives to wake up before returning
    for child in range(number_of_child_processes):
        os.wait()


def get_commands_to_execute(backup_configuration):
    '''create and return an array of commands to be executed to perform
       the rsync backups in the given configuration
    '''
    rsync_options = backup_configuration['rsync_options']
    exclude_file_directory = backup_configuration['exclude_file_directory']

    commands_to_execute = []
    for config_for_source in backup_configuration['sources']:
        source = config_for_source['source']
        exclude_file = "{}/{}".format(exclude_file_directory,
                                      config_for_source['exclude_file'])
        destinations = config_for_source['destinations']

        for destination in destinations:
            rsync_options_string = ' '.join(rsync_options)
            rsync_options_string = rsync_options_string.replace(
                                    '<<<EXCLUDE_FILE>>>',
                                    exclude_file)
            rsync_options_string = rsync_options_string.replace(
                                    '<<<SOURCE>>>', source)
            rsync_options_string = rsync_options_string.replace(
                                    '<<<DESTINATION>>>',
                                    destination)
            rsync_command = ['rsync'] + rsync_options_string.split()
            commands_to_execute.append(rsync_command)

    return commands_to_execute


def execute_backup(commands_to_execute):
    '''perform the backup.  return an array of any problems encountered'''
    problems = []
    for command in commands_to_execute:
        command_state = system_command(command,
                                       return_state=True,
                                       exception_on_error=False,
                                       echo=True)
        if command_state['status'] != 0:
            problems.append(command_state)
    return problems


def main():
    wake_up_external_drives(volume_names)

    commands_to_execute = get_commands_to_execute(backup_configuration)

    problems = execute_backup(commands_to_execute)

    if problems:
        for command_state in problems:
            print "*** PROBLEM WITH COMMAND:\n{}".format(command_state)


if __name__ == '__main__':
    sys.exit(main())
