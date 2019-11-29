运行环境:linux+python3.5
安装依赖:pip3 install -r requirements.txt
准备工作:
    cd busybox_httpd
    busybox httpd -c site.conf -p 8080 -f

程序启动:python3 file_transfer.py

单元测试:python3 unit_test.py
