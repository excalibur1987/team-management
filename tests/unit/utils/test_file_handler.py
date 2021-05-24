import io

import pytest
import requests
from faker import Faker
from flask import Flask

from app.utils.file_handler import FileHandler


def check_content(url: str, expected: str) -> bool:
    response = requests.get(url)

    return response.ok and response.content.decode() == expected


def test_handle_files(test_app: Flask, faker: Faker):
    """Tests basic operations of FileHandler class"""

    with test_app.app_context():
        test_content: str = faker.text()
        filename: str = f"{faker.name()}.txt"

        file_ = FileHandler(data=io.BytesIO(test_content.encode()), title=filename)
        file_url = file_.url
        # Check that file url has no data
        assert not requests.get(file_url).ok

        file_.save()
        # saves file and check that uploaded data is correct
        assert check_content(file_url, test_content)

        new_content: str = faker.text()
        file_.update(io.BytesIO(new_content.encode()))
        # updates file and checks against new data
        assert not check_content(file_url, test_content) and check_content(
            file_url, new_content
        )

        data_ = FileHandler(url=file_url).get_data().read().decode()
        # checks that get_data function returns valid data
        assert data_ == new_content

        file_.delete()
        # checks that file was deleted successfully and url became invalid
        assert not requests.get(file_url).ok
