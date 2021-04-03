#!/usr/bin/env python3

"""Plots turnout (votes / registered voters) by age.
Sometimes, voters have no birth date nor registration date, yet vote.
Only the ones without birth dates are thrown out, as they cannot be grouped by age.
"""

import csv
import os
from typing import Dict
from matplotlib import pyplot as plt

REGISTERED_VOTER_FOLDER = './voter_database/registered_voters'
VOTER_HISTORY_FOLDER = './voter_database/voter_history'
MINIMUM_REGISTERED_VOTERS = 50 # ages with less registered voters are not plotted.


def get_files_in_dir(dir_path: str):
    return [f'{dir_path}/{x}' for x in os.listdir(dir_path)]

def count_votes(csv_file: str, registered_voters: Dict[str, int], all_voters: Dict[str, int], election_date: str = "11/03/2020"):
    """Reads voter history CSV file and returns a map of age to the number of votes in the specified election.
    Expected CSV file columns: VoterID,ElectionDate,VotingMethod
    This updates registered_voters with voters from all_voters, if their vote was found, essentially assuming they were actually registered.
    """
    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            header = row
            break
        methods = {}
        VOTER_ID_INDEX = 0
        ELECTION_DATE_INDEX = 1
        VOTER_METHOD_INDEX = 2
        votes = {}
        unregistered = set()
        no_age = set()

        for row in csv_reader:
            if row[ELECTION_DATE_INDEX] != election_date:
                continue
            voter_id = row[VOTER_ID_INDEX]
            age = registered_voters.get(voter_id)
            if age is None:
                unregistered.add(voter_id)
                age = all_voters.get(voter_id)
                if age is None:
                    no_age.add(voter_id)
                    continue
                else:
                    # ASSUME that since vote was recorded, voter was registered,
                    # but it is just not reflected in voter roll. Update voter roll.
                    registered_voters[voter_id] = age
            if age not in votes:
                votes[age] = 0
            votes[age] += 1
            method = row[VOTER_METHOD_INDEX]
            if method not in methods:
                methods[method] = 0
            methods[method] += 1
        print(f'vote methods: {methods}')
        print(f'unregistered voters: {len(unregistered)}')
        print(f'voters with no age: {len(no_age)}')
        return votes

def count_registered_voters(registered_voters: Dict[str, int]):
    """Aggregates map of voter_id to age into a map of age to number of voters. """
    voters = {}
    for i in registered_voters:
        age = registered_voters[i]
        if age not in voters:
            voters[age] = 0
        voters[age] += 1
    return voters

def str_to_int(date: str):
    """converts MM/DD/YYYY to YYYYMMDD int for easy comparison."""
    tokens = date.strip().split('/')
    if len(tokens) != 3:
        return None
    return int(f'{tokens[-1]}{tokens[0]}{tokens[1]}')

def get_age(start: int, end: int):
    """Returns integer age given dates in form YYYYMMDD as integers. """
    diff = end - start
    if diff < 0:
        return diff / 10000.0
    else:
        return int(diff / 10000)

def get_registered_voters(csv_file: str, election_date: int = 20201103):
    """Returns a map of voter ID to age of voters registered for the specified election date.
    Expected CSV file columns:
        Precinct,LastName,FirstName,MiddleName,Suffix,
        VoterID,PolitalAff,Status,StreetNum,StreetDir,
        StreetName,StreetType,StreetPostDir,BldgNum,City,
        Zip,DateOfBirth,OriginalRegistration,MailStreet1,MailStreet2,
        MailCity,MailState,MailZip,Muni,MuniSub,
        School,SchoolSub,TechCenter,TechCenterSub,CountyComm,
        VoterHist1,HistMethod1,VoterHist2,HistMethod2,VoterHist3,
        HistMethod3,VoterHist4,HistMethod4,VoterHist5,HistMethod5,
        VoterHist6,HistMethod6,VoterHist7,HistMethod7,VoterHist8,
        HistMethod8,VoterHist9,HistMethod9,VoterHist10,HistMethod10
    """

    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)

        # skip header
        for row in csv_reader:
            header = row
            break

        VOTER_ID_INDEX = 5
        VOTER_STATUS_INDEX = 7
        DATE_OF_BIRTH_INDEX = 16
        REGISTRATION_DATE_INDEX = 17
        registered_ages = {}
        all_ages = {}

        for row in csv_reader:
            voter_id = row[VOTER_ID_INDEX]
            birth_date = row[DATE_OF_BIRTH_INDEX]
            if not birth_date:
                print(f'voter ID {voter_id} has no birth date {birth_date}')
                continue
            birth_date = str_to_int(row[DATE_OF_BIRTH_INDEX])
            if not birth_date:
                print(f'voter ID {voter_id} has invalid birth date {row[DATE_OF_BIRTH_INDEX]}')
                continue
            age = get_age(birth_date, election_date)

            assert(voter_id not in all_ages)
            all_ages[voter_id] = age

            # assume voters with no registration date are actually registered, if their status is active.
            registration_date = row[REGISTRATION_DATE_INDEX]
            if registration_date:
                registration_date = str_to_int(registration_date)
                if registration_date > election_date:
                    continue
            elif row[VOTER_STATUS_INDEX].strip() != 'A':
                continue

            assert(voter_id not in registered_ages)
            registered_ages[voter_id] = age

        print(f'registered voters: {len(registered_ages)}')
        print(f'all voters: {len(all_ages)}')
        return registered_ages, all_ages

def plot_age_distribution(voters: Dict[int, int], votes: Dict[int, int]):
    """'voters' maps age to number of registered voters. 'votes' maps age to number of votes."""
    vote_ages = set()
    for age in votes:
        vote_ages.add(age)
    voter_ages = set()
    for age in voters:
        voter_ages.add(age)
    ages = set()
    for age in voter_ages:
        if age in vote_ages:
            ages.add(age)
    ages = list(ages)
    ages.sort()
    plt.plot([x for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS], [votes[x] / voters[x] for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS])

def pair_files(files1, files2):
    """Pairs files with common prefix before '_' together."""
    groups = {}
    def prefix(filename):
        return filename.split('/')[-1].split('_')[0]
    for f in files1:
        p = prefix(f)
        if p not in groups:
            groups[p] = []
        groups[p].append(f)
    for f in files2:
        p = prefix(f)
        if p not in groups:
            groups[p] = []
        groups[p].append(f)
    pairs = []
    for p in groups:
        if len(groups[p]) != 2:
            print(f'prefix {p} not paired properly: {groups[p]}')
            continue
        groups[p].sort()
        pairs.append(groups[p])
    return pairs

if __name__ == '__main__':
    voter_files = get_files_in_dir(REGISTERED_VOTER_FOLDER)
    vote_files = get_files_in_dir(VOTER_HISTORY_FOLDER)
    pairs = pair_files(vote_files, voter_files)
    failures = set()
    for p in pairs:
        print(f'processing files {p}')
        voter_file, vote_file = p
        print(voter_file)
        try:
            registered_voters, all_voters = get_registered_voters(voter_file)
            votes = count_votes(vote_file, registered_voters, all_voters)
        except:
            failures.add(tuple(p))
            print(f'error parsing {p}')
            continue
        voters = count_registered_voters(registered_voters)
        plot_age_distribution(voters, votes)
    print(f'could not parse {len(failures)} of {len(pairs)} counties.')
    plt.xlabel(f'Age (less than {MINIMUM_REGISTERED_VOTERS} registered voters are hidden)')
    plt.ylabel('Voter turnout (votes / registered voters)')
    plt.title(f'Oklahoma Voter Turnout vs. Age ({len(pairs) - len(failures)} of {len(pairs)} counties; each line = 1 county)')
    plt.show()




