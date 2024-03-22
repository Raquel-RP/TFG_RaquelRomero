import argparse
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_user(name, uid=None, passwd=None):
    if uid is None:
        uid = 1500
    try:
        subprocess.run(['sudo', 'useradd', '-u', str(uid), name], check=True)
        logger.info(f'User "{name}" created successfully with UID {uid}.')
        if passwd:
            subprocess.run(['sudo', 'passwd', name], check=True)
            logger.info(f'Password set for user "{name}".')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error: {e.stderr.decode()}')
        sys.exit(1)

def delete_user(name):
    try:
        subprocess.run(['sudo', 'userdel', '-r', name], check=True)
        logger.info(f'User "{name}" deleted successfully.')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error: {e.stderr.decode()}')
        sys.exit(1)

def create_iptables_chain():
    try:
        subprocess.run(['sudo', 'iptables', '-N', 'COM_FILTER'], check=True)
        logger.info('iptables chain "COM_FILTER" created successfully.')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error: {e.stderr.decode()}')
        sys.exit(1)

def delete_iptables_chain():
    try:
        subprocess.run(['sudo', 'iptables', '-F', 'COM_FILTER'], check=True)
        subprocess.run(['sudo', 'iptables', '-X', 'COM_FILTER'], check=True)
        logger.info('iptables chain "COM_FILTER" deleted successfully.')
    except subprocess.CalledProcessError as e:
        logger.error(f'Error: {e.stderr.decode()}')
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Monitoring tool to filter all the network communications made by a specific user in the nflog.')
    parser.add_argument('--create-user', nargs='+', help='Create a new user. Example: --create-user name_user --uid UID --passwd PASSWORD')
    parser.add_argument('--delete-user', help='Delete an existing user.')
    parser.add_argument('--delete-iptables', action='store_true', help='Delete the iptables entries needed for the filtering.')
    parser.add_argument('--uid', type=int, help='UID of the user to monitor.')

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    try:
        if args.create_user:
            name = args.create_user[0]
            uid = int(args.create_user[2]) if len(args.create_user) > 2 else None
            passwd = args.create_user[4] if len(args.create_user) > 4 else None
            create_user(name, uid, passwd)
            create_iptables_chain()
        if args.delete_user:
            delete_user(args.delete_user)
        if args.delete_iptables:
            delete_iptables_chain()
    except KeyboardInterrupt:
        logger.warning('Process interrupted by the user.')
        sys.exit(0)

if __name__ == '__main__':
    main()
