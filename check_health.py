import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

VALIDATOR_ADDRESS = os.getenv('VALIDATOR_ADDRESS')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')

CHAINS = ['ethereum', 'binance', 'polygon', 'avalanche', 'fantom', 'moonbeam', 'aurora']


def get_all_validators():
  req_data = {"path":"/cosmos/staking/v1beta1/validators","module":"lcd"}
  response = requests.post('https://api.axelarscan.io/', json=req_data)

  return response.json()['validators']

def get_validator(validators):
  for validator in validators:
    if validator['operator_address'] == VALIDATOR_ADDRESS:
      return validator
  raise Exception('Validator not found')

def is_bonded(validator):
  return validator['status'] == 'BOND_STATUS_BONDED'

def is_jailed(validator):
  return validator['jailed']

def validator_has_external_chain(chain):
  json = {"chain": chain}
  try:
    response = requests.post('https://api.axelarscan.io/chain-maintainers', json=json)
    maintainers = response.json()['maintainers']
  except:
    return False

  return VALIDATOR_ADDRESS in maintainers

def validator_get_missing_external_chains():
  return [chain for chain in CHAINS if not validator_has_external_chain(chain)]

def send_telegram_notification(message):
  requests.post(f'https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage', json={
    'chat_id': TELEGRAM_GROUP_ID,
    'text': message,
  })

try:
  validators = get_all_validators()
except:
  sys.exit(1)

try:
  validator = get_validator(validators)
except:
  send_telegram_notification('😱 Validator not found in validators list: https://axelarscan.io/validators ⚠️⚠️⚠️')
  sys.exit(1)

if is_jailed(validator):
  send_telegram_notification('😱🧑‍⚖️👮🏽‍♀️⛓️⚖️🚨🚓🚔👮🐕‍🦺 Validator is jailed: https://axelarscan.io/validators ⚠️⚠️⚠️')

if not is_bonded(validator):
  send_telegram_notification('😱 Validator is not bonded: https://axelarscan.io/validators ⚠️⚠️⚠️')

missing_external_chains = validator_get_missing_external_chains()

for missing_chain in missing_external_chains:
  send_telegram_notification(f'😱🔗🔗🔗 Validator is missing external chain {missing_chain}: https://axelarscan.io/validators ⚠️⚠️⚠️')
