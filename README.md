# Azure backup tool
Small script to automate the process of taking shapshots of disks in Azure.
This script is pretty dumb (will target all disks), and was purpose built for the CyberForce 2019 competition.
Due to limitations in that environment, the only way to take a backup of a machine was to snapshot its disk.

Given there was at least 7 machines to defend, it required a LOT of manual clicking to backup the entire environment.
Instead of that, I wrote this small script to automate the process.

Probably not ready for production use!


## Installing
`pipenv install --pre`

## running
`pipenv run python create_snapshot.py  --resource-group-name "RESOURCE-GROUP-NAME" capture`
