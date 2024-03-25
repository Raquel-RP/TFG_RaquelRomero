#!/usr/bin/env python3

import argparse
import subprocess
import sys
import logging
import pwd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Define function to create a user
def create_user(name, uid=None, passwd=None):
    try:
        uid_option = []
        if uid is not None:
            uid_option = ['-u', str(uid)]
        
        subprocess.run(['sudo', 'useradd', *uid_option, '-m', '-s', '/bin/bash', name], check=True)
        logger.info(f'User "{name}" created successfully.')

        if passwd:
            # Open a subprocess to change the password
            passwd_process = subprocess.Popen(['sudo', 'passwd', name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Input the new password
            passwd_input = passwd.encode() + b'\n'

            passwd_process.communicate(input=2*passwd_input) # Input password and retype password

            # Check for errors
            _, stderr_data = passwd_process.communicate()
            if passwd_process.returncode != 0:
                error_message = stderr_data.decode().strip()
                if error_message:
                    logger.error(f'Error: {error_message}')
                else:
                    logger.error('Unknown error')
                sys.exit(1)
            else:
                logger.info(f'Password set for user "{name}".')

        # Get user information
        user_info = pwd.getpwnam(name)
        logger.info(f'Username: {user_info.pw_name}')
        logger.info(f'UID: {user_info.pw_uid}')

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def delete_user(name):
    try:
        subprocess.run(['sudo', 'userdel', '-r', name], check=True)
        logger.info(f'User "{name}" deleted successfully.')

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def create_iptables_chain():
    try:
        subprocess.run(['sudo', 'iptables', '-N', 'COM_FILTER'], check=True)
        subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-m', 'connmark', '--mark', '1234', '-j', 'NFLOG'])
        subprocess.run(['sudo', 'iptables', '-A', 'COM_FILTER', '-m', 'connmark', '--mark', '1234', '-j', 'NFLOG'])
        subprocess.run(['sudo', 'iptables', '-A', 'OUTPUT', '-j', 'COM_FILTER'])
        
        logger.info('iptables chain "COM_FILTER" created successfully.')
    
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

# Define function to add iptables rules
def add_iptables_rules(uid_str):
    try:
        # Verify if chain COM_FILTER already exists
        result = subprocess.run(['sudo', 'iptables', '-L', 'COM_FILTER'], capture_output=True)

        if result.returncode == 0:
            # Chain already exists, add the iptables rules without creating the chain again
            subprocess.run(['sudo', 'iptables', '-A', 'COM_FILTER', '-m', 'owner', '--uid-owner', str(uid_str), '-j', 'CONNMARK', '--set-mark', '1234'])

            logger.info('iptables rules added successfully.')
        else:
            # Chain does not exist then creates it
            create_iptables_chain()
            add_iptables_rules(uid_str)

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def delete_iptables_chain():
    try:
        subprocess.run(['sudo', 'iptables', '-D', 'INPUT', '-m', 'connmark', '--mark', '1234', '-j', 'NFLOG'], check=True)
        subprocess.run(['sudo', 'iptables', '-D', 'OUTPUT', '-j', 'COM_FILTER'],  check=True)
        subprocess.run(['sudo', 'iptables', '-F', 'COM_FILTER'], check=True)
        subprocess.run(['sudo', 'iptables', '-X', 'COM_FILTER'], check=True)

        print("Iptables rules added by com-filter.py deleted successfully.")

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def run_command(user):
    try:
        command = input("Enter the command to run: ")
        subprocess.run(['sudo', '-u', user, command], check=True)

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog='com-filter.py',
                                     usage='%(prog)s [options]',
                                     description='Tool to filter all network communications made by a specific user in NFLOG.'
)

    # Group options for the input arguments
    input_options = parser.add_argument_group('Input Variables', 'These options specify input variables but do not trigger any action.')
    input_options.add_argument('--uid', help='UID of the user to monitor.')
    input_options.add_argument('--passwd', help='Password for the new user.')
    input_options.add_argument('--user', help='User to monitor.')

    parser.add_argument('--run', nargs=1, help='Run command by a determine user. Example: --run USERNAME')
    parser.add_argument('--add', nargs=1, help='Start monitoring in NFLOG. Provide either UID or username. Example: --add [UID | USERNAME]')
    parser.add_argument('--create-user', nargs='+', help='Create a new user. Example: --create-user name_user --uid UID --passwd PASSWORD')
    parser.add_argument('--delete-user', nargs=1, help='Delete an existing user.  Example: --delete-user username')
    parser.add_argument('--delete-iptables', action='store_true', help='Delete the iptables entries needed for the filtering.')

    
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    try:
        if args.create_user:
            name = args.create_user[0]
            uid = args.uid
            passwd = args.passwd
            create_user(name, uid, passwd)

        if args.delete_user:
            delete_user(args.delete_user)

        if args.delete_iptables:
            delete_iptables_chain()
            
        if args.add:
            uid_str = args.add[0]
            add_iptables_rules(uid_str)

        if args.run:
            uid_str = args.run[0]
            run_command(uid_str)


    except KeyboardInterrupt:
        logger.warning('Process interrupted by the user.')
        sys.exit(0)

if __name__ == '__main__':
    main()
