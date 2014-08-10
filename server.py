#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import adb_manager

from tornado.options import define, options

import json

define("port", default=58848, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open('./www/index.html', 'r') as f:
            self.write(f.read())


class DeviceListHandler(tornado.web.RequestHandler):
    u"""
    ADBのデバイス一覧をJSONで返す
    """
    def get(self):
        self.set_header('Content-type', 'application/json')
        device_list = adb_manager.get_device_list()
        self.write(json.dumps(device_list))


class PackageListHandler(tornado.web.RequestHandler):
    u"""
    デバイスのパッケージ一覧を返す
    """
    def get(self):
        device_id = self.get_argument('device_id')
        self.set_header('Content-type', 'application/json')
        package_list = adb_manager.get_package_list(device_id)
        self.write(json.dumps(package_list))


class UninstallPackageFromDevice(tornado.web.RequestHandler):
    u"""
    デバイスの指定パッケージをアンインストール
    """
    def get(self):
        device_id = self.get_argument('device_id')
        package_name = self.get_argument('package_name')
        self.set_header('Content-type', 'application/json')

        uninstall_response = adb_manager.uninstall_package_from_device(device_id, package_name)
        result = {
            'response': uninstall_response
        }
        self.write(json.dumps(result))


class GetPackageIconSrcFromGooglePlay(tornado.web.RequestHandler):
    u"""
    指定パッケージのアイコンURLをGooglePlayから取得する。
    パッケージが取得できない場合は、android_icon.pngを返す
    JSON形式
    """
    def get(self):
        package_name = self.get_argument('package_name')
        icon_size = self.get_argument('icon_size', 300)

        self.set_header('Content-type', 'application/json')

        result = {
            'package': package_name
        }
        try:
            # Google PlayのHTMLを取得し、アイコンのsrcを取得する。いつか動かなくなる
            # パッケージがない、インデックスが異常になったりするとexceptに飛ぶ
            import urllib2
            url = 'http://play.google.com/store/apps/details?id=%s' % package_name
            response = urllib2.urlopen(url)
            html = response.read()
            index_quote_left_image = html.index('<div class="cover-container">')
            index_quote_left_image += html[index_quote_left_image:].index('<img class="cover-image"')
            index_quote_left_image += html[index_quote_left_image:].index('src="')
            index_quote_left_image += len('src="')
            index_quote_right_image = html[index_quote_left_image:].index('"')
            image_src = html[index_quote_left_image:index_quote_left_image + index_quote_right_image]

            if (icon_size != 300) and (image_src.endswith('w300')):
                image_src = image_src.replace('w300', 'w'+icon_size)

            result['image_src'] = image_src

        except Exception as e:
            result['error'] = e.message
            result['image_src'] = '/android_icon.png'

        self.write(json.dumps(result))


class ConnectWearHandler(tornado.web.RequestHandler):
    u"""
    Android WearをBluetoothデバッグで接続する
    """
    def get(self):
        self.set_header('Content-type', 'text/plain')
        connect_result = adb_manager.connect_wear_bluetooth()
        self.write(connect_result)


class StartPackageHandler(tornado.web.RequestHandler):
    u"""
    指定パッケージを起動する…が成功していない。
    """
    def get(self):
        device_id = self.get_argument('device_id')
        package_name = self.get_argument('package_name')
        self.set_header('Content-type', 'application/json')
        connect_result = adb_manager.start_package(device_id, package_name)
        self.write(connect_result)


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/devices", DeviceListHandler),
        (r"/packages", PackageListHandler),
        (r"/package-icon", GetPackageIconSrcFromGooglePlay),
        (r"/uninstall-package", UninstallPackageFromDevice),
        (r"/connect-wear-debug", ConnectWearHandler),
        # (r"/start-package", StartPackageHandler),

        # to avoid templates
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./www/"}),
    ])

    print "server starting at PORT=%d" % options.port

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)

    # サーバー開始時にブラウザを起動する
    import webbrowser
    webbrowser.open('http://localhost:%d/' % options.port)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
