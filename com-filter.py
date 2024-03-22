import argparse
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_user(name, uid=None, passwd=None):
    try:
        uid_option = []
        if uid is not None:
            uid_option = ['-u', str(uid)]
        
        subprocess.run(['sudo', 'useradd', *uid_option, '-m', '-s', '/bin/bash', name], check=True)
        logger.info(f'User "{name}" created successfully.')

        if passwd:
            # Open a subprocess to change password
            passwd_process = subprocess.Popen(['sudo', 'passwd', name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Input the new password
            passwd_input = passwd.encode() + b'\n'
            passwd_process.communicate(input=passwd_input)

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
        logger.info('iptables chain "COM_FILTER" created successfully.')
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def add_iptables_rules(uid):
    try:
        subprocess.run(['sudo', 'iptables', '-A', 'COM_FILTER', '-m', 'owner', '--uid-owner', str(uid), '-j', 'CONNMARK', '--set-mark', '1'])
        subprocess.run(['sudo', 'iptables', '-A', 'COM_FILTER', '-m', 'connmark', '--mark', '1234', '-j', 'NFLOG'])
        subprocess.run(['sudo', 'iptables', '-A', 'COM_FILTER', '-m', 'connmark', '--mark', '1234', '-j', 'NFLOG'])
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def delete_iptables_chain():
    try:
        subprocess.run(['sudo', 'iptables', '-F', 'COM_FILTER'], check=True)
        subprocess.run(['sudo', 'iptables', '-X', 'COM_FILTER'], check=True)
        logger.info('iptables chain "COM_FILTER" deleted successfully.')
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f'Error: {error_message}')
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Monitoring tool to filter all the network communications made by a specific user in the nflog.')
    parser.add_argument('--create-user', nargs='+', help='Create a new user. Example: --create-user name_user --uid UID --passwd PASSWORD')
    parser.add_argument('--delete-user', help='Delete an existing user.')
    parser.add_argument('--delete-iptables', action='store_true', help='Delete the iptables entries needed for the filtering.')
    parser.add_argument('--uid', type=int, help='UID of the user to monitor.')
    parser.add_argument('--passwd', help='Password for the new user.')

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
            
        if args.uid:
            uid = int(args.uid)
            create_iptables_chain()
            add_iptables_rules(uid)


    except KeyboardInterrupt:
        logger.warning('Process interrupted by the user.')
        sys.exit(0)

if __name__ == '__main__':
    main()
