import unittest
from unittest.mock import MagicMock
import check_health

MOCK_VALIDATOR_ADDRESS = 'axelarvaloper1u024xjdxs2yxmez5tv77v7qe2e7ygazy385dr9'

from unittest.mock import Mock

def assert_not_any_called_with(self, *args, **kwargs):
    try:
        self.assert_any_call(*args, **kwargs)
    except AssertionError:
        return
    raise AssertionError('Expected %s to not have been called.' % self._format_mock_call_signature(args, kwargs))

MagicMock.assert_not_any_called_with = assert_not_any_called_with

check_health.send_telegram_notification = MagicMock()
check_health.VALIDATOR_ADDRESS = MOCK_VALIDATOR_ADDRESS
check_health.is_missing_chain = MagicMock(return_value=False)
check_health.CHAINS = ['ethereum']

class TestMessages(unittest.TestCase):
    def test_validator_missing(self):
        check_health.get_all_validators = MagicMock(return_value=[])

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['validator_missing']['error_message'])
        check_health.send_telegram_notification.reset_mock()

        check_health.check()
        check_health.send_telegram_notification.assert_not_any_called_with(check_health.errors['validator_missing']['error_message'])

        validator = {'operator_address': MOCK_VALIDATOR_ADDRESS, 'status': 'BOND_STATUS_BONDED', 'jailed': False}
        check_health.get_all_validators = MagicMock(return_value=[validator])

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['validator_missing']['recover_message'])

    def test_validator_jailed(self):
        validator = {'operator_address': MOCK_VALIDATOR_ADDRESS, 'status': 'BOND_STATUS_BONDED', 'jailed': True}
        check_health.get_all_validators = MagicMock(return_value=[validator])

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['jailed']['error_message'])
        check_health.send_telegram_notification.reset_mock()

        check_health.check()
        check_health.send_telegram_notification.assert_not_any_called_with(check_health.errors['jailed']['error_message'])

        validator['jailed'] = False
        check_health.get_all_validators = MagicMock(return_value=[validator])

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['jailed']['recover_message'])

    def test_validator_bonded(self):
        validator = {'operator_address': MOCK_VALIDATOR_ADDRESS, 'status': 'BOND_STATUS_UNBONDED', 'jailed': False}
        check_health.get_all_validators = MagicMock(return_value=[validator])

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['bonded']['error_message'])
        check_health.send_telegram_notification.reset_mock()

        check_health.check()
        check_health.send_telegram_notification.assert_not_any_called_with(check_health.errors['bonded']['error_message'])

        validator['status'] = 'BOND_STATUS_BONDED'
        check_health.get_all_validators = MagicMock(return_value=[validator])

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['bonded']['recover_message'])

    def test_validator_missing_chain(self):
        validator = {'operator_address': MOCK_VALIDATOR_ADDRESS, 'status': 'BOND_STATUS_BONDED', 'jailed': False}
        check_health.get_all_validators = MagicMock(return_value=[validator])
        check_health.is_missing_chain = MagicMock(return_value=True)

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['missing-chain-ethereum']['error_message'])
        check_health.send_telegram_notification.reset_mock()

        check_health.check()
        check_health.send_telegram_notification.assert_not_any_called_with(check_health.errors['missing-chain-ethereum']['error_message'])

        check_health.is_missing_chain = MagicMock(return_value=False)

        check_health.check()
        check_health.send_telegram_notification.assert_any_call(check_health.errors['missing-chain-ethereum']['recover_message'])


if __name__ == '__main__':
    unittest.main()
