#!/usr/bin/env python3
"""Secret-Santa-O-Matic (for Python)

This script allows the user to generate and print to the console a sequence
of names that represents a gift giving order for secret santa. Includes the
possibility to set invalid (i.e. forbidden) combinations.

Author: Matthias Budde 2022 - 2023

This file can also be imported as a module and contains the `Santa` class 
with the following functions:

    * register_recipient
    * delete_recipient
    * generate_sequence - randomly draws a secret santa sequence

Additonally, when not imported as a module, this file executes some example
code illustrating its use:

    * main - the main function of the script
"""

#TODO This script requires that `logging` be installed within the Python
#environment you are running this script in.

#TODO Will terminate after 20 tries if no valid sequence can be found.

__version__ = '0.03'

import random
import logging
import yaml

sso_logger = logging.getLogger('secretsantaomatic')
sso_log_lvl = logging.getLevelName('INFO')
sso_logger.setLevel(sso_log_lvl) # log level for mylogger

class Santa:
    def __init__(self, candidate_dict:dict = {}):
        self.__recipient_list = list(candidate_dict.keys())
        self.__forbidden_recipients = {k: set(v) for k, v in candidate_dict.items() if v is not None}
        self.__sequence = []
        self.__sort_recipients_by_no_of_candidates()

    def __str__(self) -> str:
        #TODO return meaningful string representation for printing
        return f'Secret santa for {self.__recipient_list}'

    def get_recipients(self) -> list:
        """Returns list of currently registered recipients.
        """
        return self.__recipient_list

    def get_forbidden_recipients(self) -> dict:
        """Returns dict of forbidden recipients for all candidates.
        """
        return self.__forbidden_recipients

    def get_sequence(self) -> list:
        """Returns current sequence.
        """
        return self.__sequence

    def register_recipient(self, name: str, forbidden_recipients: list = None):
        """Adds a new recipient to Santa's candidate list, optionally with a list 
           of people whom they should not give gifts to.
        """
        if name.casefold() in (recipient.casefold() for recipient in self.__recipient_list):
            print(f'Someone by the name of {name} is already in the recipient list!')
        else:
            self.__recipient_list.append(name)
            if forbidden_recipients is not None:
                self.__forbidden_recipients.update({name: forbidden_recipients}) 
        self.__sort_recipients_by_no_of_candidates()
        #TODO Update or invalidate __sequence

    def delete_recipient(self, name: str, cascade: bool = False):
        """Removes the named recipient from Santa's candidate list.
        """
        if name in self.__recipient_list:
            self.__recipient_list.remove(name)
            self.__forbidden_recipients.pop(name, None)
        if cascade:
            for k,v in list(self.__forbidden_recipients.items()):
                v.discard(name)
                if not v:
                    self.__forbidden_recipients.pop(k, None)
        self.__sort_recipients_by_no_of_candidates()
        #TODO Update or invalidate __sequence

    def __draw_lots(self, max_tries = 25) -> list:
        """Creates a random secret santa sequence from Santa's candidate list.
        Begins with the candidate who has the fewest possible giftees and then
        continues to randomly draw from the remaining ones until a valid loop
        is found or the retry count reaches the maximum. 

        Parameters
        ----------
        max_tries: int, optional
            maximum number of attemps to find a valid sequence before giving up.

        Returns
        ------
        Secret santa sequence as list of names. Last element is first name again.
        Returns empty set if no valid sequence can be found.
        """
        result_sequence = []
        fail_count = 0
        while not result_sequence and fail_count < max_tries:
            print(f'Fail count is {fail_count}')
            candidate_list = self.__recipient_list.copy()
            first_recipient = candidate_list.pop(0)
            result_sequence = [first_recipient]
            previous_candidate = first_recipient
            while candidate_list:
                possible_giftees = self.__get_possible_recipients(candidate_list, previous_candidate)
                if possible_giftees:
                    candidate_name = random.choice(possible_giftees)
                    result_sequence.append(candidate_name)
                    candidate_list.remove(candidate_name)
                    print(f'{previous_candidate} gives gift to {candidate_name}')
                    previous_candidate = candidate_name
                else:
                    print('No candidate left for current recipient, starting over...')
                    fail_count += 1
                    result_sequence = []
                    break
            # check if last and first in sequence are a valid combination
            if result_sequence:
                if not first_recipient in self.__forbidden_recipients.get(previous_candidate, []):
                    result_sequence.append(first_recipient)
                else:
                    print('Last and first recipients are not a valid pairing, starting over...')
                    fail_count += 1
                    result_sequence = []
        return result_sequence
  
    def __get_possible_recipients(self, giftee_list:list, gifter_name:str) -> list:
        """Returns a dictionary of possible candidate recipients from the passed
        recipient list for the named gifter.
        """
        return list(set(giftee_list).difference(self.__forbidden_recipients.get(gifter_name, []), [gifter_name]))
 
    def __sort_recipients_by_no_of_candidates(self):
        """Sorts recipient list by number of possible candidates ascending.
        """
        candidate_dict = { k: self.__get_possible_recipients(self.__recipient_list, k) for k in self.__recipient_list }
        self.__recipient_list = sorted(candidate_dict, key=lambda k: len(candidate_dict[k]), reverse=False)
 
    def __sequence_possible(self) -> bool:
        #TODO implement function to check if it may be impossible to generate a sequence. Is this possible?
        #first, check number of recipients, less than two and not possible
        #second, check number of possible recipients for candidate with least options, if zero then impossible
        # (actually this encompasses option 1, so first check is probably unnecessary)
        #third, check for each ...?
        return True

    def generate_sequence(self):
        self.__sequence = self.__draw_lots()
        return self.__sequence


def write_sequence(sequence: list, write_path:str='.'):
    """writes the passed sequence to files."""
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

def main():
    # Load options
    options = yaml.safe_load(open('./config.yml'))
    outpath = options.get('outpath', '.')

    """Main function to demo."""
    candidates = options.get('candidates')

    ssom = Santa(candidates)

    sequence = []
    while not sequence:
        sequence = ssom.generate_sequence()
    #write_sequence(sequence, outpath)
    print(sequence)

if __name__ == '__main__':
    main()
