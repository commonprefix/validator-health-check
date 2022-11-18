import requests
import os
from dotenv import load_dotenv

load_dotenv()

VALIDATOR_ADDRESS = os.getenv('VALIDATOR_ADDRESS')
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
VALIDATOR_NAME = os.getenv('VALIDATOR_NAME')
AXELARSCAN_API_URL = os.getenv('AXELARSCAN_API_URL')

CHAINS = os.getenv('EXTERNAL_CHAINS').split(',')

errors = {
  'bonded': {
    'error_message': '😱 Validator is not bonded: https://axelarscan.io/validators ⚠️⚠️⚠️',
    'recover_message': '✅ Validator is bonded again: https://axelarscan.io/validators',
    'last_status': False
  },
  'jailed': {
    'error_message': '😱🧑‍⚖️👮🏽‍♀️⛓️⚖️🚨🚓🚔👮🐕‍🦺 Validator is jailed: https://axelarscan.io/validators ⚠️⚠️⚠️',
    'recover_message': '✅ Validator is unjailed: https://axelarscan.io/validators',
    'last_status': False
  },
  'validator_missing': {
    'error_message': '😱 Validator not found in validators list: https://axelarscan.io/validators ⚠️⚠️⚠️',
    'recover_message': '✅ Validator back in validators list: https://axelarscan.io/validators',
    'last_status': False
  }
}

for chain in CHAINS:
  errors[f'missing-chain-{chain}'] = {
    'error_message': f'😱🔗🔗🔗 Validator is missing external chain {chain}: https://axelarscan.io/validators ⚠️⚠️⚠️',
    'recover_message': f'✅ Validator external chain {chain} is registered again: https://axelarscan.io/validators',
    'last_status': False
  }

def get_all_validators():
  all_validators = []
  req_data = {'path':'/cosmos/staking/v1beta1/validators', 'module':'lcd'}
  while True:
    response = requests.post(AXELARSCAN_API_URL, json=req_data)
    response_json = response.json()

    all_validators = all_validators + response_json['validators']
    pagination_key = response_json['pagination']['next_key']

    if pagination_key == None:
      break

    req_data['pagination.key'] = pagination_key

  return all_validators

def get_validator(validator_address, validators):
  for validator in validators:
    if validator['operator_address'] == validator_address:
      return validator
  raise Exception('Validator not found')

def is_bonded(validator):
  return validator['status'] == 'BOND_STATUS_BONDED'

def is_jailed(validator):
  return validator['jailed']

def is_missing_chain(validator_address, chain):
  try:
    req_data = {'path':'/chain-maintainers', 'chain': chain}
    response = requests.post(f'{AXELARSCAN_API_URL}/chain-maintainers', json=req_data)
    maintainers = response.json()['maintainers']
  except:
    return False

  return validator_address not in maintainers

def send_telegram_notification(message):
  message = f'[{VALIDATOR_NAME}] {message}'
  print(message)
  requests.post(f'https://api.telegram.org/bot{TELEGRAM_API_KEY}/sendMessage', json={
    'chat_id': TELEGRAM_GROUP_ID,
    'text': message,
  })


def handle_error_status(error_name, error_status):
  if (error_status == errors[error_name]['last_status']):
    return

  if error_status:
    send_telegram_notification(errors[error_name]['error_message'])
  else:
    send_telegram_notification(errors[error_name]['recover_message'])

  errors[error_name]['last_status'] = error_status


def check():
  try:
    validators = get_all_validators()
  except:
    return
  
  try:
    validator = get_validator(VALIDATOR_ADDRESS, validators)
    handle_error_status('validator_missing', False)
  except:
    handle_error_status('validator_missing', True)
    return

  handle_error_status('jailed', is_jailed(validator))

  handle_error_status('bonded', not is_bonded(validator))

  for chain in CHAINS:
    handle_error_status(f'missing-chain-{chain}', is_missing_chain(VALIDATOR_ADDRESS, chain))
