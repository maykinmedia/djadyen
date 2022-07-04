import os


class TestFileMixin:
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "files")

    def _get_test_file(self, name):
        """
        Loads files from the test_dir directory by default to be used during tests
        """
        path = os.path.join(self.test_dir, name)

        if not os.path.exists(path):
            raise OSError(f"{path} does not exist")

        file = open(path, "rb")

        self.addCleanup(lambda file: file.close(), file)

        return file

    def _get_json_data(self, name):
        return self._get_test_file(name).read().decode("utf-8")
