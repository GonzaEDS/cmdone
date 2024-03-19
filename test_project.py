import pytest
from project import file_name_to_title, split_type, error_msg, error_msg_retry
from rich.console import Console

@pytest.fixture
def mock_console(mocker):
    console_mock = mocker.patch.object(Console, 'print')
    return console_mock

def test_file_name_to_title():
    assert file_name_to_title("my_document.csv") == "My Document"
    assert file_name_to_title("another_test_file.csv") == "Another Test File"

def test_split_type():
    assert split_type("Name(@ID)") == ("Name", "(@ID)")
    assert split_type("Some Title(@TEXT)") == ("Some Title", "(@TEXT)")
    assert split_type("Invalid") == (None, None)


def test_error_msg_retry(mock_console):
    error_msg_retry("An error occurred")
    mock_console.assert_called_once_with('[italic][bright_red]An error occurred, try again[bright_red][/italic]')

def test_error_msg(mock_console):
    error_msg("Simple error")
    mock_console.assert_called_once_with('[italic][bright_red]Simple error[bright_red][/italic]')
