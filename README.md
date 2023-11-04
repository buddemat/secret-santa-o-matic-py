# secret-santa-o-matic-py

This project is a Python version of my `perl` script [secret-santa-o-matic](https://github.com/buddemat/secret-santa-o-matic), a program to automatically determine a random sequence of Secret Santas for a list of people. 

It is possible to exclude certain people from being gift recipients for others, e.g. if two people are a couple and they and will be giving gifts to each other already anyway.

:bangbang:   
:bangbang: This software is under construction, so not everything's here yet...  
:bangbang:   

## Usage
Before generating a sequence of secret santas, the list of people from whom said sequence should be built needs to be configured.

### Configuration
To generate a sequence for a list of people, add those people in the config file `config.yml`. For each person, insert a key under the 1st level key `candidates`. If the respective
persons should be excluded as secret santa for certain people, add a list of these as 
value for the respective name.

##### Example `candidates` section:

```yaml
candidates:
    Alice: [Bob]
    Bob: [Alice]
    Charlene:
    David:
```

This will generate a secret santa sequence of four people (Alice, Bob, Charlene, and David). Alice and Bob are not supposed to give gifts to each other in this scenario.

### Execution

Once the recipients are configured, simply run

```python
$ python secretsantaomatic.py
```

The resulting sequence will be written to individual files which can then be emailed as attachments to the individual recipients without knowing who gets whom.

## Repository structure


```bash
secret-santa-o-matic-py
├── LICENSE                     # License TODO
├── README.md                   # This file.
└── secretsantaomatic
    ├── ascii_tree.txt          # ASCII art file that is appended to secret santa txt files.
    ├── config.yml              # Configuration and list of people 
    ├── __init__.py
    ├── santas                  # Target directory for secret santa txt files
    │   └── README.md
    └── secretsantaomatic.py    # Module to generate secret santa sequence.
```
