#!/usr/bin/env python3

import argparse
import subprocess
import sys
import pwd
import logging
import random
import iptc
import signal

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

rule1 = iptc.Rule()
rule2 = iptc.Rule()
rule3 = iptc.Rule()

input_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
output_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")

user_exists = False

# Define function to create a user
def create_user(name):
    
    print("Creating new user...")
    
    try:
        subprocess.run(
            ["sudo", "useradd", "-m", "-s", "/bin/bash", name], check=True
        )
        logger.info(f'User "{name}" created successfully.')

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f"Error: {error_message}")
        sys.exit(1)

def delete_user(name):
    try:
        subprocess.run(["sudo", "userdel", "-r", name], check=True, text=True)
        logger.info(f'User "{name}" deleted successfully.')

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f"Error: {error_message}")
        sys.exit(1)


# Define function to add iptables rules
def add_iptables_rules(uid_str):
    try:
        # Generates a random mark value in between 0 and 65535 (0xffff)
        random_mark = random.randint(0, 65535)
        mark = format(random_mark, '#06x')

        # Rule to filter by user UID
        match1 = iptc.Match(rule1, "owner")
        match1.uid_owner = uid_str
        rule1.target = iptc.Target(rule1, "CONNMARK")
        rule1.target.set_mark = mark
        rule1.add_match(match1)

        # Rule to send the inputs to the NFLOG
        match2 = iptc.Match(rule2, "connmark")
        match2.mark = mark
        rule2.target = iptc.Target(rule2, "NFLOG")
        rule2.add_match(match2)

        # Rule to send the outputs to the NFLOG
        match3 = iptc.Match(rule3, "connmark")
        match3.mark = mark
        rule3.target = iptc.Target(rule3, "NFLOG")
        rule3.add_match(match3)

        output_chain.insert_rule(rule1)
        input_chain.insert_rule(rule2)
        output_chain.insert_rule(rule3)
        
        logger.info("Iptables rules added successfully.")

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f"Error: {error_message}")
        sys.exit(1)


def delete_iptables():
    try:
        output_chain.delete_rule(rule1)
        input_chain.delete_rule(rule2)
        output_chain.delete_rule(rule3)

        print("Iptables rules added by com-filter.py deleted successfully.")

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f"Error: {error_message}")
        sys.exit(1)


def check_user_exists(username):
    global user_exists
    
    try:
        pwd.getpwnam(username)  
        user_exists = True
        print(f"User '{username}' exists.")
    except KeyError:
        user_exists = False
        print(f"User '{username}' does not exist.")
        

def cleanup(user_str):
    if user_exists == False:
        delete_user(user_str)
    delete_iptables()
    

def main():
    parser = argparse.ArgumentParser(
        prog="com-filter.py",
        usage="%(prog)s [options]",
        description="Tool to filter all network communications made by a determined user to the NFLOG.",
    )

    # Group options for the input arguments
    input_options = parser.add_argument_group(
        "Input Variables",
        "These options specify input variables but do not trigger any action.",
    )
    #input_options.add_argument("--uid", help="UID of the user to monitor.")
    #input_options.add_argument("--passwd", help="Password for the new user.")
    #input_options.add_argument("--user", help="User to monitor.")

    # Default argument
    parser.add_argument("username", nargs='?', help="Username to run the command")

    # Optional arguments
    parser.add_argument(
        "-c", "--create-user",
        nargs='?',
        help="Create a new user. Example: --create-user username",
    )
    parser.add_argument(
        "-d", "--delete-user",
        nargs='?',
        help="Delete an existing user.  Example: --delete-user username",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    try:
        if not any(vars(args).values()):
            parser.print_help()
            sys.exit(0)

        if args.create_user:
            name = args.create_user[0]
            create_user(name)

        if args.delete_user:
            delete_user(args.delete_user)

        if args.username:
            user_str = args.username
            check_user_exists(user_str)
            if user_exists == False:
                create_user(user_str)
            add_iptables_rules(user_str)
            signal.pause()

    except KeyboardInterrupt:
        print("KeyboardInterrupt received")
        cleanup(user_str)
        sys.exit(0)


if __name__ == "__main__":
    main()
