#!/usr/bin/env python3

import argparse
import subprocess
import sys
import pwd
import logging
import secrets
import iptc
import signal
import shlex

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Initialize iptables rules
rule1 = iptc.Rule()
rule2 = iptc.Rule()
rule3 = iptc.Rule()

# Define iptables chains
input_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
output_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")

# Initialize user and group status flags
user_exists = False
group_id = False


# Define function to create a user
def create_user(name):

    logger.info("Creating new user...")

    try:
        sanitized_name = shlex.quote(name)  # Sanitize the name input
        subprocess.run(
            ["/usr/bin/sudo", "/usr/sbin/useradd", "-s", "/bin/bash",
             sanitized_name],
            check=True,
        )
        logger.info(f'User "{name}" created successfully.')

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f"Error: {error_message}")
        sys.exit(1)


# Define function to delete a user
def delete_user(name):
    logger.debug(f'Deleting user "{name}"...')

    try:
        sanitized_name = shlex.quote(name)  # Sanitize the name input
        subprocess.run(
            ["/usr/bin/sudo", "/usr/sbin/userdel", sanitized_name],
            check=True,
            text=True,
        )
        logger.info(f'User "{name}" deleted successfully.')

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        logger.error(f"Error: {error_message}")
        sys.exit(1)


# Define function to add iptables rules
def add_iptables_rules(uid_str, group):

    logger.debug("Adding iptables rules...")

    try:
        # Generates a random mark value in between 0 and 65535 (0xffff) using
        # a cryptographically secure random generator
        random_mark = secrets.randbelow(65536)
        mark = format(random_mark, "#06x")

        # Rule to filter by user UID
        match1 = iptc.Match(rule1, "owner")
        match1.uid_owner = uid_str
        rule1.target = iptc.Target(rule1, "CONNMARK")
        rule1.target.set_mark = mark
        rule1.add_match(match1)

        # Rule to send the inputs to the NFLOG
        match2 = iptc.Match(rule2, "connmark")
        match2.mark = mark
        rule2.add_match(match2)
        target_rule2 = rule2.create_target("NFLOG")

        # Adds NFLOG group if indicated
        if group_id:
            target_rule2.set_parameter("nflog-group", str(group))
            logger.debug("NFLOG group added in INPUT rule succesfully.")

        rule2.target = target_rule2

        # Rule to send the outputs to the NFLOG
        match3 = iptc.Match(rule3, "connmark")
        match3.mark = mark
        rule3.add_match(match3)
        target_rule3 = rule3.create_target("NFLOG")

        # Adds NFLOG group if indicated
        if group_id:
            target_rule3.set_parameter("nflog-group", str(group))
            logger.debug("NFLOG group added in OUTPUT rule succesfully.")

        rule3.target = target_rule3

        # Insert rules into the chains
        output_chain.insert_rule(rule1)
        logger.debug("Rule 1 added succesfully.")

        input_chain.insert_rule(rule2)
        logger.debug("Rule 2 added succesfully.")

        output_chain.insert_rule(rule3)
        logger.debug("Rule 3 added succesfully.")

        logger.info("Iptables rules added successfully.")

    except iptc.IPTCError as e:
        error_message = str(e)
        logger.error(f"Error: {error_message}")
        sys.exit(1)


# Define function to delete iptables rules
def delete_iptables():

    logger.debug("Deleting iptables rules...")

    try:
        output_chain.delete_rule(rule1)
        input_chain.delete_rule(rule2)
        output_chain.delete_rule(rule3)

        logger.info(
            "Iptables rules added by com-filter.py deleted successfully."
            )

    except iptc.IPTCError as e:
        error_message = str(e)
        logger.error(f"Error: {error_message}")
        sys.exit(1)


# Define function to check if a user exists
def check_user_exists(username):
    global user_exists

    try:
        pwd.getpwnam(username)
        user_exists = True
        logger.info(f"User '{username}' exists.")

    except KeyError:
        user_exists = False
        logger.info(f"User '{username}' does not exist.")


# Define cleanup function
def cleanup(user_str):
    if user_exists is False:
        delete_user(user_str)
    delete_iptables()


# Define main function
def main():
    parser = argparse.ArgumentParser(
        prog="com-filter.py",
        usage="%(prog)s [options]",
        description=(
            "Tool to filter all network communications made by a "
            "determined user to the NFLOG."
        ),
    )

    # Default argument
    parser.add_argument("username", nargs="?",
                        help="Username to run the command")

    # Optional arguments
    parser.add_argument(
        "-g",
        "--group",
        nargs=1,
        help="Creates an NFLOG group. Example: --group 2",
    )
    parser.add_argument(
        "-c",
        "--create-user",
        nargs="?",
        help="Create a new user. Example: --create-user username",
    )
    parser.add_argument(
        "-d",
        "--delete-user",
        nargs="?",
        help="Delete an existing user.  Example: --delete-user username",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    args = parser.parse_args()

    # Set logging level to DEBUG if verbose flag is set
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    try:
        # If no arguments are provided, print help message
        if not any(vars(args).values()):
            parser.print_help()
            sys.exit(0)

        # Handle create-user option
        if args.create_user:
            name = args.create_user
            create_user(name)

        # Handle delete-user option
        if args.delete_user:
            delete_user(args.delete_user)

        # Handle username argument
        if args.username:
            user_str = args.username
            check_user_exists(user_str)
            if user_exists is False:
                create_user(user_str)
            if args.group:
                global group_id
                group_id = True
                group = args.group[0]
                add_iptables_rules(user_str, group)
            else:
                add_iptables_rules(user_str, None)

            # Process suspenssion
            signal.pause()

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
        cleanup(user_str)
        sys.exit(0)


# Execute main function if script is run directly
if __name__ == "__main__":
    main()
