# Checking for Voting Machine Fraud in the State of Oklahoma

This checks for patterns between voter turnout and age in Oklahoma in the 2020 General Presidential Election.

## Setup

Requires python3. Before running, be sure you have enough free space for the downloaded CSV files and converted JSON files. Should be about 2 GB for all 77 counties in Oklahoma.

## Running

1. Obtain voter list. The data is free, but you must first request access: https://oklahoma.gov/elections/candidate-info/voter-list.html
2. Rename the voter registry folder to `./voter_database/registered_voters`
3. Rename the voter history folder to `./voter_database/voter_history`
4. Plot voter turnout lines vs. age for all counties on the same plot: `./plot_turnout_by_age.py`

## Data source

Links are hard-coded in the python code and may break if websites are changed.

Ohio voter registration database: https://www6.ohiosos.gov/ords/f?p=VOTERFTP:HOME:::#cntyVtrFiles

