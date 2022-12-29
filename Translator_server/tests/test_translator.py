import pytest
from mock import patch, Mock
from mock.mock import PropertyMock

# Format of tests cases: test_method_scenario_expected-behaviour
# Example test_sum_2plus5_7returned

from my_translator import MyTranslator


def test_translator_initialization():
    with patch('my_translator.Translator') as mock_google_translator:
        translator = MyTranslator()
        assert translator is not None
        mock_google_translator.assert_called_with(service_urls=['translate.google.com'])

def test_translator_serialization():
    pass

def test_translate_default_hello():
    with patch('my_translator.Translator') as mock_google_translator:
        given_value = "hello"
        expected_value = "привіт"
        # mock the translate method of the Translator
        mock_translate_method = mock_google_translator.return_value.translate
        mock_translate_method.return_value.text = expected_value

        translator = MyTranslator()
        translated_value = translator.translate(given_value)

        assert translated_value == expected_value
        mock_translate_method.assert_called_with(given_value, dest="uk", src="auto")

def test_translate_specified_all_parameters():
    with patch('my_translator.Translator') as mock_google_translator:
        given_value = "привіт"
        given_kwargs = {"dest": "en", "src": "ua"}
        expected_value = "hello"

        # mock the translate method of the Translator
        mock_translate_method = mock_google_translator.return_value.translate
        mock_translate_method.return_value.text = expected_value

        translator = MyTranslator()
        translated_value = translator.translate(given_value, **given_kwargs)

        assert translated_value == expected_value
        mock_translate_method.assert_called_with(given_value, **given_kwargs)

