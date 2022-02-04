# ens-domains-all:
Get all ens domains that are about to expire.

# Infura IDs:

1. 2735dcf2e7694898afdd1c3fabe09a4b
2. 8bc45d5a46fd4bef97abf7a1a90dce1d
3. 56d62a0bc884483fbc7a6b37e7e4a117

# Usage:

`python3 ens_info.py --t domains_info --d 30 --id 2735dcf2e7694898afdd1c3fabe09a4b` - get all domains that are about to expire in 30 days

`python3 ens_info.py --t get_domains --id 8bc45d5a46fd4bef97abf7a1a90dce1d` - get list of all domains

`python3 ens_info.py --t both --d 30` - first get all domains then get all domains that are about to expire in 30 days
