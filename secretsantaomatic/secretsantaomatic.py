#!/usr/bin/env python3
"""Secret-Santa-O-Matic (for Python)

This script allows the user to generate and print to the console a sequence
of names that represents a gift giving order for secret santa. Includes the
possibility to set invalid (i.e. forbidden) combinations.

Author: Matthias Budde 2022 - 2023

This file can also be imported as a module and contains the following
functions:

    * draw_lots - randomly draws a secret santa sequence
    * main - the main function of the script
"""

#TODO This script requires that `logging` be installed within the Python
#environment you are running this script in.

#TODO Will terminate after 20 tries if no valid sequence can be found.

__version__ = '0.03'

import random
import logging
import yaml

# Load options
options = yaml.safe_load(open('./config.yml'))

sso_logger = logging.getLogger('secretsantaomatic')
sso_log_lvl = logging.getLevelName('INFO')
sso_logger.setLevel(sso_log_lvl) # log level for mylogger

class Santa:
    def __init__(self, candidate_dict:dict = {}):
        self.recipient_set = set(candidate_dict.keys())
        self.forbidden_recipients = {k: set(v) for k, v in candidate_dict.items() if v is not None}
        self.sequence = []

    def __str__(self) -> str:
        #TODO return meaningful string representation for printing
        return f'Secret santa for {self.recipient_set}'

    def register_recipient(self, name: str, forbidden_recipients: list = None):
        if name.casefold() in (recipient.casefold() for recipient in self.recipient_set):
            print(f'Someone by the name of {name} is already in the recipient list!')
        else:
            self.recipient_set.add(name)
            if forbidden_recipients is not None:
                self.forbidden_recipients.update({name: set(forbidden_recipients)}) 

    def delete_recipient(self, name: str, cascade: bool = False):
        self.recipient_set.discard(name)
        if cascade:
            for k,v in list(self.forbidden_recipients.items()):
                v.discard(name)
                if not v:
                    self.forbidden_recipients.pop(k, None)

    def __draw_lots(self, max_tries = 10) -> list:
        candidate_set = self.recipient_set.copy()
        result_sequence = []
        previous_candidate = None
        fail_count = 0
        while candidate_set:
            candidate_name = random.choice(tuple(candidate_set))
            if not candidate_name in self.forbidden_recipients.get(previous_candidate, []):
                result_sequence.append(candidate_name)
                candidate_set.remove(candidate_name)
                previous_candidate = candidate_name
                fail_count = 0
            else:
                print('Candidate invalid!')
                fail_count += 1
            if fail_count >= max_tries:
                result_sequence = []
                break
        # check if last and first in sequence are a valid combination
        if result_sequence:
            first_recipient = result_sequence[0]
            if not first_recipient in self.forbidden_recipients.get(previous_candidate, []):
                result_sequence.append(first_recipient)
            else:
                result_sequence = []
        return result_sequence

    def __is_valid_sequence(self, sequence: list):
        #TODO
        return False

    def generate_sequence(self):
        self.sequence = self.__draw_lots()


def draw_lots(candidate_dict: dict) -> list:
    """Creates a random secret santa sequence from a candidate list.

    Parameters
    ----------
    candidate_dict : dict, mandatory
        dict with names from whom a secret santa sequence should be drawn.
        The candidate names are the keys and the (optional) values are a list
        of candidates that should not receive gifts from the respective candidate.

    Returns
    ------
    Secret santa sequence as list of names. Last element is first name again.
    Returns empty set if no valid sequence can be found.
    """
    candidate_set = set(candidate_dict.keys())
    forbidden_recipients = {k: v for k, v in candidate_dict.items() if v is not None}
    result_sequence = []
    previous_candidate = None
    fail_count = 0
    while candidate_set:
        candidate_name = random.choice(tuple(candidate_set))
        if not candidate_name in forbidden_recipients.get(previous_candidate, []):
            result_sequence.append(candidate_name)
            candidate_set.remove(candidate_name)
            previous_candidate = candidate_name
            fail_count = 0
        else:
            print('Candidate invalid!')
            fail_count += 1
        if fail_count >= 10:
            result_sequence = []
            break
    # check if last and first in sequence are a valid combination
    if result_sequence:
        first_recipient = result_sequence[0]
        if not first_recipient in forbidden_recipients.get(previous_candidate, []):
            result_sequence.append(first_recipient)
        else:
            result_sequence = []
    return result_sequence

def write_sequence(sequence: list):
    """writes the passed sequence to files."""
    write_path = options.get('outpath', '.')
    for gifter, recipient in zip(sequence, sequence[1:]):
        #print(gifter, recipient)
        with open(f'{write_path}/{gifter}.txt', 'w', encoding = 'utf-8') as outfile:
            outfile.write('')
            outfile.write(f'Hello {gifter}!\n\n')
            outfile.write('This text file has been automatically generated by' \
                          f' Secret-Santa-O-Matic for Python {__version__}\n\n')
            outfile.write('You are secret santa for ... (drumroll) ...\n\n')
            outfile.write(f'     {recipient}\n\n')
            outfile.write('Enjoy! And please don\'t tell anyone!\n')
            if options.get('asciiartpath'):
                with open(options.get('asciiartpath'), 'r', encoding='utf-8') as asciiart:
                    outfile.write(asciiart.read())

# # TODO: write function to dynamically load people
# def register_recipient(name: str, forbidden_recipients: list = None):
#     """Add a recipient, optionally with a list of people whom they should not give gifts to."""
#     pass

def main():
    """Main function to demo."""
    candidates = options.get('candidates')

    sequence = []
    while not sequence:
        sequence = draw_lots(candidates)
    write_sequence(sequence)

if __name__ == '__main__':
    main()
