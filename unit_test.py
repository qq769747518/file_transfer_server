import unittest
from file_transfer import *

download_module=File_download_module('LiLei','ILoveHanMeimei')

upload_module= File_upload_module('yangqun369', 'qq18351342479')

class TestMathFunc(unittest.TestCase):

    def test_download_file(self):
        """
        测试从busybox站点下载文件功能
        :return:
        """
        self.assertEqual('download file successful', download_module.download_file('msg.txt'))

    def test_get_user_cookies(self):
        """
        测试从pastebin网站获取用户cookie功能
        :return:
        """
        self.assertEqual('get user cookies successful', upload_module.get_user_cookies())

    def test_get_csrf_token(self):
        """
        测试从pastebin网站获取文件提交表单中的csrf_token功能
        :return:
        """
        self.assertEqual('get csrf token successful', upload_module.get_csrf_token())

    def test_upload_file(self):
        """
        测试上传文件功能
        :return:
        """
        self.assertEqual('upload file successful', upload_module.upload_file('127.0.0.1_msg.txt'))

if __name__ == '__main__':
    unittest.main()
