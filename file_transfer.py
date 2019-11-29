import collections
import re
import requests
import base64

from hyper.contrib import HTTP20Adapter
from requests_toolbelt import MultipartEncoder


class File_download_module():

    def __init__(self, busy_username, busy_password, busy_ip='127.0.0.1', busy_port='8080', file_folder='./'):
        """
        :param busy_username:busybox站点的用户名
        :param busy_password:busybox站点的密码
        :param busy_ip:busybox站点的IP
        :param busy_port:busybox站点的端口号
        :param file_folder:下载文件的本地保存路径
        """
        self.busy_ip = busy_ip
        self.file_folder = file_folder
        self.busy_username = busy_username
        self.busy_password = busy_password
        # 获取经base64编码的用户名和密码,并转化为str类型
        self.__authorization = base64.b64encode('{}:{}'.format(busy_username, busy_password).encode()).decode()
        self.busy_url = 'http://{}:{}'.format(busy_ip, busy_port)

    def download_file(self, file_name):
        """
        从busybox站点下载指定文件,并保存在本地
        :param file_name只能是文本文件,以.txt结尾:
        :return:local_file_path 下载文件在本地的保存路径
        """
        file_url = self.busy_url + '/' + file_name
        local_file_path = self.file_folder + '{}_{}'.format(self.busy_ip, file_name)
        try:
            response = requests.get(file_url,
                                    headers={
                                        'Authorization': 'Basic ' + self.__authorization
                                    },
                                    stream=True  # 以流的形式下载文件,防止大文件占用过多内存
                                    )
        except Exception as e:
            return 'Network request error,The error message:{}'.format(e)
        if response.status_code == 404:
            return '{} error,{}not find '.format(file_name, file_name)
        if response.status_code == 401:
            return '{} or {} error '.format(self.busy_username, self.busy_password)
        with open(local_file_path, "wb") as f:
            # 一次读取1024字节的文本写入本地文件
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return 'download file successful'


class File_upload_module():

    def __init__(self, user_name, user_password):
        """
        :param user_name: pastebin网站的用户名
        :param user_password:pastebin网站的用户密码
        """
        self.user_name = user_name
        self.user_password = user_password
        self.sessions = requests.Session()
        self.sessions.mount('https://pastebin.com', HTTP20Adapter())
        self.cookies = {'pastebin_user': ''}
        self.csrf_token = ''
        self.boundary = '----WebKitFormBoundary4P7JmtBiDbjSJYzM'

    def get_user_cookies(self):
        '''
        获取用户的cookie值,保存为对象属性cookie过期时间180天
        :return:
        '''
        url = 'https://pastebin.com/login'
        headers = {
            ':authority': 'pastebin.com',
            ':method': 'POST',
            ':path': '/login',
            ':scheme': 'https',
            'cache-control': 'max-age=0',
            'content-length': '89',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://pastebin.com',
            'referer': 'https://pastebin.com/login',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        data = {
            'submit_hidden': 'submit_hidden',
            'user_name': self.user_name,
            'user_password': self.user_password,
            'submit': 'Login'}
        try:
            response = self.sessions.post(url, headers=headers, data=data)
        except Exception as e:
            return 'Network request error,The error message:{}'.format(e)
        if 'pastebin_user' not in response.headers[b'set-cookie'].decode():
            return '{},{} error or login failed'.format(self.user_name, self.user_password)
        cookies = response.headers[b'set-cookie'].decode()
        pastebin_user_cookie = cookies.split(';')[0]
        pastebin_user = pastebin_user_cookie.split('=')[1]
        self.cookies['pastebin_user'] = pastebin_user
        return 'get user cookies successful'

    def get_csrf_token(self):
        """
        获取文件提交表单中的csrf_token值,保存为对象属性,用于提交表单请求
        :return:
        """
        url = 'https://pastebin.com/'
        headers = {
            ':authority': ' pastebin.com',
            ':method': 'GET',
            ':path': '/',
            ':scheme': 'https',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://pastebin.com/',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        try:
            response = self.sessions.get(url, headers=headers)
        except Exception as e:
            return 'Network request error,The error message:{}'.format(e)
        reg = r'<input type="hidden" name="csrf_token_post" value="(.*)">'
        pattern = re.compile(reg)
        result = pattern.findall(response.text)
        self.csrf_token = result[0]
        return 'get csrf token successful'

    def upload_file(self, local_file_path, paste_format='1', paste_expire_date='N', paste_private='0', paste_name=''):
        """
        :param local_file_path: 要上传内容的文件路径
        :param paste_format:主要语言
        :param paste_expire_date:过期时间
        :param paste_private:属性
        :param paste_name:名字
        :return:
        """
        url = 'https://pastebin.com/post.php'
        headers = {
            ':authority': 'pastebin.com',
            ':method': 'POST',
            ':path': '/post.php',
            ':scheme': 'https',
            'content-length': '820',
            'content-type': 'multipart/form-data;boundary={}'.format(self.boundary),
            'origin': 'https://pastebin.com',
            'pragma': 'no-cache',
            'referer': 'https://pastebin.com/',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
        }
        try:
            with open(local_file_path, 'rb') as f:
                paste_code = f.read()
        except Exception as e:
            return 'read {} error,The error message:{}'.format(local_file_path, e)
        dic = collections.OrderedDict()
        dic['csrf_token_post'] = self.csrf_token
        dic['submit_hidden'] = 'submit_hidden'
        dic['paste_code'] = paste_code
        dic['paste_format'] = paste_format
        dic['paste_expire_date'] = paste_expire_date
        dic['paste_private'] = paste_private
        dic['paste_name'] = paste_name
        # 构造表单数据,并用boundary分割不同部分
        multipart_encoder = MultipartEncoder(fields=dic, boundary=self.boundary)
        response = self.sessions.post(url, headers=headers, data=multipart_encoder, cookies=self.cookies)
        location_path = response.headers[b'location'].decode()
        if 'php' in location_path:
            return 'upload file failed'
        else:
            return 'upload file successful'


if __name__ == '__main__':
    download_module = File_download_module('LiLei', 'ILoveHanMeimei')

    #可使用自己的用户名,密码进行验证
    upload_module = File_upload_module('yangqun369', 'qq18351342479')

    download_result = download_module.download_file('msg.txt')
    assert download_result == 'download file successful', download_result
    print(download_result)

    get_user_cookies_result = upload_module.get_user_cookies()
    assert get_user_cookies_result == 'get user cookies successful', get_user_cookies_result
    print(get_user_cookies_result)

    get_csrf_token_result = upload_module.get_csrf_token()
    assert get_csrf_token_result == 'get csrf token successful', get_csrf_token_result
    print(get_csrf_token_result)

    upload_file_result = upload_module.upload_file('127.0.0.1_msg.txt')
    print(upload_file_result)
