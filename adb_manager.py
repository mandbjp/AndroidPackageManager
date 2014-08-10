# coding=utf-8
import subprocess


def get_device_list():
    u"""
    adbコマンドで接続されているデバイス一覧を取得する
    :return: [{device_id, device_status}, ...]
    """

    command = 'adb devices'
    print command
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    parse_state = 0
    device_list = []
    for line in p.stdout.readlines():
        # 改行を削除
        line = line.rstrip()
        print line
        if parse_state == 0:
            if line.index('List of devices') != -1:
                parse_state = 1
                continue

        elif parse_state == 1:
            if len(line) != 0:
                [device_id, status] = line.split('\t', 1)
                device_list.append({
                    'device_id': device_id,
                    'status':    status,
                })
    print 'subprocess done.'

    return devices


def get_package_list(device_id):
    u"""
    指定デバイスのパッケージ一覧を取得する
    :param device_id string AndroidDeviceId
    :return: {device_id, packages:[package_name, ...]}
    """

    command = 'adb -s %s shell pm list packages' % device_id
    print command
    packages = []
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stdout.readlines():
        # 改行を削除
        line = line.rstrip()
        print line
        if line.startswith('package:'):
            packages.append(line[len('package:'):])
    print 'subprocess done.'

    packages.sort()
    result = {
        'device_id': device_id,
        'packages':  packages
    }
    return result


def uninstall_package_from_device(device_id, package_name):
    u"""
    指定デバイス、指定パッケージをアンインストールする
    :param device_id string AndroidDeviceId
    :param device_id string com.android.chrome
    :return: 'Success', 'Failure'
    """
    command = 'adb -s %s shell pm uninstall %s' % (device_id, package_name)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stdout.readlines():
        # 改行を削除
        line = line.rstrip()
        return line


def connect_wear_bluetooth():
    u"""
    Android WearをBluetooth経由で接続する
    :return: 'connected to localhost:4444', 'already connected to localhost:4444'
    """
    commands = [
        'adb forward tcp:4444 localabstract:/adb-hub',
        'adb connect localhost:4444'
    ]
    result = []
    for command in commands:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in p.stdout.readlines():
            # 改行を削除
            line = line.rstrip()
            result.append(line)

    # 改行区切りの文字列に変換
    return '\n'.join(result)


def start_package(device_id, package_name):
    u"""
    指定デバイス、指定パッケージを開始する
    :param device_id string AndroidDeviceId
    :param device_id string com.android.chrome
    :return: {}
    """

    command = 'adb -s %s shell am start intent.action.MAIN -n %s' % (device_id, package_name)
    print command
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in p.stdout.readlines():
        # 改行を削除
        line = line.rstrip()
        print line
    print 'subprocess done.'

    result = {
    }
    return result


if __name__ == '__main__':
    devices = get_device_list()
    package_list = get_package_list(devices[0]['device_id'])
