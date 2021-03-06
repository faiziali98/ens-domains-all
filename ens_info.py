from web3 import Web3, HTTPProvider
from ens import ENS
from datetime import datetime,timedelta
import argparse
import time
import requests
import sys


# Run it once
def get_all_domains(w3, ns):
	contract_address = '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e'

	print("Starting scan for domains, all domains will be written on domains.txt file")

	x_start = 9488108
	page = 3
	stop = 0

	while stop != 1:
		try:
			with open('last_call.txt', 'r') as f_inp:
				line = f_inp.readlines()[-1]
				if line:
					splits = line.split(',')
					x_start = int(splits[0])
					page = int(splits[1])
			
			# Start from current blocknumber and go down w3.eth.blockNumber
			for x in range(x_start, w3.eth.blockNumber, 100000):
				unique_addresses = []

				while True:
					url = f'https://api.etherscan.io/api?module=account&action=txlist&address={contract_address}&startblock={x}&endblock={x+100000}&page={page}&offset=100&apikey=YSI4UU7642M1V7QSF7E9UT1FQBYVANNW7U'
					res = requests.get(url, timeout=12.50)
					unique_domains = []

					with open('last_call.txt', 'w') as lc:
						lc.write(url)
						lc.write(f'\n{x},{page}')


					print(url)

					if res.status_code == 200:
						data = res.json()

						if data["message"] == "No transactions found":
							page = 1
							break
						else:
							print(len(data['result']))
							for result in data['result']:
								try:
									address = result['from']

									if address not in unique_addresses:
										domain_found = ns.name(address)
										unique_addresses.append(address)
										if domain_found:
											unique_domains.append(domain_found)
								except KeyboardInterrupt:
									sys.exit()
								except:
									print("Infura Max Reached")

						with open('domains.txt', 'a+') as f:
							for unique_domain in unique_domains:
								f.write(f"{unique_domain}\n")

					page += 1

				if x%100 == 0:
					print(x)

			print("Finished scanning the domains")
			stop = 1
		except KeyboardInterrupt:
			sys.exit()
		except:
			print("Trying again")

# Get expiry of domain from smart contract
def get_domain_expiry(domain_name, grace_period, contract_instance):
	primary_name = domain_name.split('.')[-2]

	print(primary_name)

	# Calling smart contract
	time = contract_instance.functions.nameExpires(Web3.toInt(Web3.keccak(text=primary_name))).call()

	# return expiry + grace period
	return time + grace_period

	

def get_about_to_expire_domains(grace, contract_instance, days_range):
	# Open a file containing all domains
	with open('domains.txt', 'r+') as domains:
		# Open file with required domains
		with open('required_domains.csv', 'a') as f:
			for domain in domains:
				# Get domain name
				domain_name = domain.strip()

				# Get domain expiry + grace period
				domain_expiry = get_domain_expiry(domain_name, grace, contract_instance)

				# Get current + 60 days
				date_now = datetime.now()
				date_to_check = date_now + timedelta(days_range)
				date_to_check = time.mktime(date_to_check.timetuple())
				date_now = time.mktime(date_now.timetuple())

				# Put domain in file if about to expire
				if (domain_expiry >= date_now and domain_expiry <= date_to_check):
					f.write(f"{domain_name}, {datetime.utcfromtimestamp(domain_expiry).strftime('%Y-%m-%d %H:%M:%S')}\n")



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="PROG")

	# Adding two arguments
	parser.add_argument("--id", default="8bc45d5a46fd4bef97abf7a1a90dce1d", help="Input infura project id")
	parser.add_argument("--t", default="get_domains", help="Enter run type")
	parser.add_argument("--d", default="60", help="Enter run type")
	args = parser.parse_args()

	# Get w3 provider
	w3 = Web3(HTTPProvider(f'https://mainnet.infura.io/v3/{args.id}'))

	# Get Name space
	ns = ENS.fromWeb3(w3)

	# Get Smart contract of BaseRegistrarImplementation.sol
	address = '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85'
	abi = '[{"inputs":[{"internalType":"contract ENS","name":"_ens","type":"address"},{"internalType":"bytes32","name":"_baseNode","type":"bytes32"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"controller","type":"address"}],"name":"ControllerAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"controller","type":"address"}],"name":"ControllerRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"id","type":"uint256"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint256","name":"expires","type":"uint256"}],"name":"NameMigrated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"id","type":"uint256"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint256","name":"expires","type":"uint256"}],"name":"NameRegistered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"id","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"expires","type":"uint256"}],"name":"NameRenewed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"GRACE_PERIOD","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"controller","type":"address"}],"name":"addController","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"available","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"baseNode","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"controllers","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"ens","outputs":[{"internalType":"contract ENS","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"isOwner","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"nameExpires","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"name":"reclaim","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"duration","type":"uint256"}],"name":"register","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"duration","type":"uint256"}],"name":"registerOnly","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"controller","type":"address"}],"name":"removeController","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"duration","type":"uint256"}],"name":"renew","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"resolver","type":"address"}],"name":"setResolver","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes4","name":"interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
	contract_instance = w3.eth.contract(address=address, abi=abi)

	# Get grace period from smart contract
	grace = contract_instance.functions.GRACE_PERIOD().call()

	if (args.t == 'get_domains'):
		get_all_domains(w3, ns)
	elif (args.t == 'domains_info'):
		get_about_to_expire_domains(grace, contract_instance, int(args.d))
	elif (args.t == 'both'):
		get_all_domains(w3, ns)
		get_about_to_expire_domains(grace, contract_instance, int(args.d))
	else:
		print("Kindly provide a valid run type")
