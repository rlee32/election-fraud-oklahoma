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

ELECTION_YEAR = 2020 # choose presidential election years from 2000 - 2020

ELECTION_DAY = {
    2020: '03',
    2016: '08',
    2012: '06',
    2008: '04',
    2004: '02',
    2000: '07'
}

ELECTION_MONTH = '11'
ELECTION_DATE_STR = f'{ELECTION_MONTH}/{ELECTION_DAY[ELECTION_YEAR]}/{ELECTION_YEAR}'
ELECTION_DATE_INT = int(f'{ELECTION_YEAR}{ELECTION_MONTH}{ELECTION_DAY[ELECTION_YEAR]}')

def get_files_in_dir(dir_path: str):
    return [f'{dir_path}/{x}' for x in os.listdir(dir_path) if x[0] != '.'] # ignore hidden files.

def count_votes(csv_file: str, registered_voters: Dict[str, int], all_voters: Dict[str, int]):
    """Reads voter history CSV file and returns a map of age to the number of votes in the specified election.
    Expected CSV file columns: VoterID,ElectionDate,VotingMethod
    This updates registered_voters with voters from all_voters, if their vote was found, essentially assuming they were actually registered.
    """
    with open(csv_file, 'r', encoding='latin-1') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            header = row
            break
        methods = {}
        VOTER_ID_INDEX = header.index('VoterID')
        ELECTION_DATE_INDEX = header.index('ElectionDate')
        VOTER_METHOD_INDEX = header.index('VotingMethod')
        votes = {}
        unregistered = set()
        no_age = set()

        for row in csv_reader:
            if row[ELECTION_DATE_INDEX] != ELECTION_DATE_STR:
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

def get_registered_voters(csv_file: str):
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

    with open(csv_file, 'r', encoding='latin-1') as f:
        csv_reader = csv.reader(f)

        # skip header
        for row in csv_reader:
            header = row
            break

        VOTER_ID_INDEX = header.index('VoterID')
        VOTER_STATUS_INDEX = header.index('Status')
        DATE_OF_BIRTH_INDEX = header.index('DateOfBirth')
        REGISTRATION_DATE_INDEX = header.index('OriginalRegistration')
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
            age = get_age(birth_date, ELECTION_DATE_INT)

            assert(voter_id not in all_ages)
            all_ages[voter_id] = age

            # assume voters with no registration date are actually registered, if their status is active.
            registration_date = row[REGISTRATION_DATE_INDEX]
            if registration_date:
                registration_date = str_to_int(registration_date)
                if registration_date > ELECTION_DATE_INT:
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
    overall_turnout = sum(votes) / sum(voters)
    plt.plot([x for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS], [votes[x] / voters[x] / overall_turnout for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS])

import sys
import json
from generate_key import OUTPUT_FILE as KEY_FILE

if __name__ == '__main__':

    county_id = sys.argv[1]

    key = json.load(open(KEY_FILE, 'r'))

    voter_file = f'{REGISTERED_VOTER_FOLDER}/CTY{county_id}_vr.csv'
    vote_file = f'{VOTER_HISTORY_FOLDER}/CTY{county_id}_vh.csv'

    registered_voters, all_voters = get_registered_voters(voter_file)
    votes = count_votes(vote_file, registered_voters, all_voters)
    voters = count_registered_voters(registered_voters)

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

    overall_turnout = sum(votes) / sum(voters)
    plt.plot([x for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS], [votes[x] for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS], 'r-')
    plt.plot([x for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS], [voters[x] * overall_turnout * key[str(x)] for x in ages if voters[x] > MINIMUM_REGISTERED_VOTERS], 'b:')

    plt.xlabel(f'Age (less than {MINIMUM_REGISTERED_VOTERS} registered voters are hidden)')
    plt.ylabel('Votes cast (red line is actual, blue line is prediction)')
    plt.title(f'{ELECTION_YEAR} Oklahoma County ID {county_id}: Votes Cast vs. Age')
    plt.show()




