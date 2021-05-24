import io
import uuid
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError
from flask import current_app


class FileHandlerInterface:
    data: io.BytesIO
    name: str
    public: bool
    file_url: str
    file_args: Dict[str, str]
    file_object: Any

    def __init__(
        self, data: io.BytesIO, name: str, public: bool = False, url: str = None
    ) -> None:
        pass

    def get_data(self) -> io.BytesIO:
        pass

    def _get_fileobj_fromurl(self) -> None:
        pass

    def _create_fileobj(self) -> None:
        pass

    def _create_url(self, file_key: str) -> str:
        pass

    def save(
        self,
    ) -> None:
        pass

    def delete(
        self,
    ) -> None:
        pass

    def update(self, data: io.BytesIO) -> None:
        pass


class FileHandler:
    handler: FileHandlerInterface
    url: str

    def __init__(
        self,
        data: io.BytesIO = None,
        title: str = None,
        public: bool = False,
        url: str = None,
    ) -> None:
        """Registers a FileHandler proxy based on app configuration

        Args:
            data (io.BytesIO, optional): File contents as bytes. Defaults to None.
            title (str, optional): Filename. Defaults to None.
            public (bool, optional): Make the url public. Defaults to False.
            url (str, optional): Used to handle uploaded files if data is not provided. Defaults to None.
        """
        storage_handlers = {"s3": FileHandlerS3}
        self.handler = storage_handlers[current_app.config["STORAGE_TARGET"]](
            data,
            title,
            public,
            url,
        )

    def __repr__(self) -> str:
        self.handler.__repr__()

    def save(
        self,
    ) -> None:
        """Saves the file to provider"""

        self.handler.save()

    @property
    def url(self):
        """url to download file"""
        return self.handler.file_url

    def get_data(self) -> io.BytesIO:
        """returns the file as bytes"""

        return self.handler.get_data()

    def delete(self) -> None:
        """Deletes file from provider"""
        self.handler.delete()

    def update(self, data: io.BytesIO) -> None:
        """Updates file contents with same url"""
        self.handler.update(data=data)


class FileHandlerS3(FileHandlerInterface):
    data: io.BytesIO
    title: str
    public: bool
    file_args: dict
    file_url: str

    def __init__(
        self, data: io.BytesIO, title: str, public: bool = False, url: str = None
    ) -> None:
        self.data = data
        self.title = title
        self.public = public
        self.file_args = {} if not public else {"ACL": "public-read"}
        self.file_url = url

        self.file_object = self._create_fileobj()
        self.file_url = self._create_url(self.file_object.key)

    def __repr__(self) -> str:
        return self.file_url

    def _get_resource(self):
        protocol = (
            "https" if current_app.config["FLASK_ENV"] == "production" else "http"
        )
        s3_resource = boto3.resource(
            "s3",
            endpoint_url=f"{protocol}://" + current_app.config["AWS_ENDPOINT"],
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        )

        return s3_resource

    def _get_fileobj_fromurl(
        self,
    ) -> Any:
        s3_resource = self._get_resource()
        return s3_resource.Object(
            current_app.config["S3_BUCKET_NAME"], self.file_url.split("/")[-1]
        )

    def _create_fileobj(self) -> Any:
        if self.file_url:
            return self._get_fileobj_fromurl()
        s3_resource = self._get_resource()
        random_file_name = "".join([str(uuid.uuid4().hex[:6]), self.title])
        return s3_resource.Object(
            current_app.config["S3_BUCKET_NAME"], random_file_name
        )

    def _create_url(self, file_key: str) -> str:
        protocol = (
            "https" if current_app.config["FLASK_ENV"] == "production" else "http"
        )

        return f"{protocol}://s3-{current_app.config['AWS_REGION']}.{current_app.config['AWS_ENDPOINT']}/{current_app.config['S3_BUCKET_NAME']}/{file_key}"

    def save(
        self,
    ) -> str:

        self.file_object.upload_fileobj(
            io.BytesIO(self.data.read()), ExtraArgs=self.file_args
        )
        self.data.seek(0)

    def delete(self):

        try:
            if self.file_object.content_length > 0:
                _ = self.file_object.delete()
            return True
        except ClientError:
            return False

    def update(self, data: io.BytesIO) -> None:
        self.data = None
        self.file_object.upload_fileobj(data)

    def get_data(self) -> io.BytesIO:
        if self.data:
            return self.data
        obj = self._get_fileobj_fromurl()
        temp_file = io.BytesIO()
        obj.download_fileobj(temp_file)

        temp_file.seek(0)

        return temp_file
