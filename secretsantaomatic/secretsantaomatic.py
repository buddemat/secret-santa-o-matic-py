#!/usr/bin/env python3
"""Secret-Santa-O-Matic (for Python)

This module allows the user to generate and print to the console a sequence
of names that represents a gift giving order for secret santa. Includes the
possibility to set invalid (i.e. forbidden) combinations.

Author: Matthias Budde 2022 - 2023

This file can be imported as a module and contains the `Santa` class
with the following functions:

    * register_recipient
    * delete_recipient
    * generate_sequence - randomly draws a secret santa sequence

Additonally, when not imported as a module, this file executes some example
code illustrating its use:

    * main - the main function of the script, will terminate after 25 tries
             if no valid sequence can be found.
"""

#TODO This script requires that `logging` be installed within the Python
#environment you are running this script in.


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

    def get_recipients(self) -> list[str]:
        """Returns list of currently registered recipients.
        """
        return self.__recipient_list

    def get_forbidden_recipients(self) -> dict:
        """Returns dict of forbidden recipients for all candidates.
        """
        return self.__forbidden_recipients

    def get_sequence(self) -> list[str]:
        """Returns current sequence.
        """
        return self.__sequence

    def register_recipient(self, name: str, forbidden_recipients: list[str] = None) -> bool:
        """Adds a new recipient to Santa's candidate list, optionally with a list
           of people whom they should not give gifts to.

        Parameters
        ----------
        name: str
            name of the recipient that should be added to the list.
        forbidden_recipients: list[str], optional
           list of forbidden giftees, i.e. names for whom the added recipient 
           should not be a gifter.

        Returns
        -------
        `True` if the recipient was successfully added, `False` if someone by
        the name of `name` already exists.

        Examples
        --------
        >>> santa.register_recipient('Alice')
        >>> santa.register_recipient('Bob', ['Alice'])
        """
        if name.casefold() in (recipient.casefold() for recipient in self.__recipient_list):
            print(f'Someone by the name of {name} is already in the recipient list!')
            return False
        else:
            self.__recipient_list.append(name)
            if forbidden_recipients is not None:
                self.__forbidden_recipients.update({name: forbidden_recipients})
        self.__sort_recipients_by_no_of_candidates()
        #TODO Update or invalidate __sequence
        return True

    def delete_recipient(self, name: str, cascade: bool = False):
        """Removes the named recipient from Santa's candidate list as well as
        their list of forbidden recipients.

        Parameters
        ----------
        name: str
            name of the recipient that should be removed.
        cascade: bool, optional
            if `True`, the recipient will also be removed from all remaining
            recipients' lists of forbidden giftees.
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

    def __draw_lots(self, max_tries = 25) -> list[str]:
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

    def __get_possible_recipients(self, giftee_list:list[str], gifter_name:str) -> list[str]:
        """Returns a dictionary of possible candidate recipients from the passed
        recipient list for the named gifter.
        """
        return list(set(giftee_list).difference(self.__forbidden_recipients.get(gifter_name, []), [gifter_name]))

    def __sort_recipients_by_no_of_candidates(self):
        """Sorts recipient list by number of possible candidates ascending.
        """
        candidate_dict = { k: self.__get_possible_recipients(self.__recipient_list, k) for k in self.__recipient_list }
        self.__recipient_list = sorted(candidate_dict, key=lambda k: len(candidate_dict[k]), reverse=False)
        # return something?

    def __sequence_possible(self) -> bool:
        #first, check number of recipients, less than two means not possible
        if len(self.__recipient_list) < 2:
            print(f'Not enough recipients registered with Santa ({len(self.__recipient_list)}).')
            return False
        #second, check number of possible recipients for candidate with least options, if zero then impossible
        if not self.__get_possible_recipients(self.__recipient_list, self.__recipient_list[0]):
            print(f'There is at least one gifter with no valid giftees ("{self.__recipient_list[0]}").')
            return False
        #TODO implement further checks if it may be impossible to generate a sequence. Is this possible?
        #third, check for each ...?
        return True

    def generate_sequence(self) -> list[str]:
        if not self.__sequence_possible():
            print('No sequence possible with current candidate list. Please reconfigure.')
        else:
            self.__sequence = self.__draw_lots()
            if not self.__sequence:
                print('No valid sequence could be found, maybe it\'s not possible with the configured recipients?')
        return self.__sequence


def write_sequence(sequence: list[str], write_path:str='.'):
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
    """Main function to demo."""
    # Load options
    options = yaml.safe_load(open('./config.yml', encoding='utf-8'))
    outpath = options.get('outpath', '.')

    candidates = options.get('candidates')

    ssom = Santa(candidates)

    sequence = ssom.generate_sequence()
    #write_sequence(sequence, outpath)
    print(sequence)

if __name__ == '__main__':
    main()
