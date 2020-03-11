import os
import subprocess
import tempfile
import time
import re

emulator_names = [
    'pixel_10.0',
    'pixel_9.0',
    'pixel_8.0',
    'pixel_7.1',
    'pixel_7.0',
    'pixel_6.0',
]


def kill_emulator_process():
    subprocess.check_output('adb emu kill', shell=True)


def start_emulator(emulator_name):
    ''' Starts an emulator and returns a reference to it, given its name.'''

    os.environ.get('ANDROID_SDK_ROOT')
    print('Starting emulator:', emulator_name)
    command = 'emulator -avd %s -wipe-data -debug surface'
    emulator = subprocess.Popen(command % emulator_name,
                                stdout=tempfile.TemporaryFile(),
                                stderr=subprocess.STDOUT,
                                shell=True)
    return emulator


def wait_for_output(open_emulator, expected_output, seconds_to_wait):
    starting_time = time.time()

    for line in iter(open_emulator.stdout.readline, ''):
        if expected_output in line:
            break
        else:
            elapsed_seconds = time.time() - starting_time
            if elapsed_seconds > seconds_to_wait:
                raise Exception("Waited more than %d seconds for output %s"
                                % (seconds_to_wait, expected_output))


def wait_for_boot_completed(seconds_to_wait):
    starting_time = time.time()

    device_status = b''
    while device_status != b'stopped':
        try:
            device_status = subprocess.check_output('adb shell getprop init.svc.bootanim',
                                                    stderr=subprocess.DEVNULL)
            device_status = device_status.rstrip()
        except subprocess.CalledProcessError as e:
            pass

        elapsed_seconds = time.time() - starting_time
        if elapsed_seconds > seconds_to_wait:
            raise Exception("Waited more than %d seconds for loading android %s"
                            % (seconds_to_wait, emulator_name))


def get_sample_apks():
    apk_path = os.path.abspath('cohtml/NativeSamples/Unpacked/Samples/Android/')
    android_apk_files = []

    for root, dirs, files in os.walk(apk_path):
        for file in files:
            if file.endswith('.apk'):
                android_apk_files.append(os.path.join(root, file))
    return android_apk_files


def convert_to_activity_name(apk_name):
    filename = os.path.split(apk_name)[-1]
    regex = '(Sample.*)-(gles\d)'
    match = re.search(regex, filename)
    return match.group(1) + 'Activity'


def get_gles_version(apk_name):
    if 'gles2' in apk_name:
        backend_version = 'gles2'
    elif 'gles3' in apk_name:
        backend_version = 'gles3'
    else:
        raise Exception('Only apps with GLES backend are supported. App: %s' % backend_name)
    return backend_version


def run_hello_cohtml_test():
    subprocess.check_output('python cohtml/Samples/Tests/SampleHelloCohtml.py',
                            shell=True)


def run_nameplates_test():
    subprocess.check_output('python cohtml/Samples/Tests/SampleNameplates.py',
                            shell=True)


def close_app(gles_version):
    subprocess.check_output('adb shell pm clear com.coherentlabs.coherentsample.%s'
                            % gles_version, shell=True)
    print('Apk closed')


def uninstall_app(gles_version):
    subprocess.check_output('adb uninstall com.coherentlabs.coherentsample.%s'
                            % gles_version, shell=True)
    print('Uninstall successful')
    kill_emulator_process()
    print('The emulator was closed')
    print('-'*70)


def start_sample(activity_name, gles_version):
    '''Starts an app, forwards the port and runs tests.
    When test are done, closes and uninstalls the app.'''

    subprocess.check_output('adb shell am start -n com.coherentlabs.coherentsample.%s/'
                            'com.coherentlabs.coherentsample.%s'
                            % (gles_version, activity_name), shell=True)
    subprocess.check_output('adb forward tcp:9444 tcp:9444')


def check_for_crashes():
    print('Checking for crashes...')
    check = subprocess.check_output('adb logcat -b crash --regex DEBUG --max-count 100 --print -d',
                            shell=True)
    for new_line in check.split(b'\n'):
        print('%r' % new_line)


def run_tests(activity_name, gles_version):
    if activity_name == 'SampleHelloCohtmlActivity':
        run_hello_cohtml_test()
    elif activity_name == 'SampleNameplatesActivity':
        run_nameplates_test()
    else:
        raise Exception('Unknown sample')

    close_app(gles_version)
    uninstall_app(gles_version)


def install_apk(apk_name):
    print('Installing:', os.path.split(apk_name)[-1])
    subprocess.check_output('adb install ' + apk_name, shell=True)
    print('Install successful')


def verify_android_apk(apk, emulator_name):
    '''Opens an emulator, then gets and installs an apk.
    Gives information about app backend and activity to start tests.'''

    emulator = start_emulator(emulator_name)

    try:
        # wait_for_boot_completed has to go twice because, Android 9.0 returns 'stopped' before it is loaded
        wait_for_boot_completed(300)
        wait_for_boot_completed(300)
        install_apk(apk)

        gles_version = get_gles_version(apk)
        activity_name = convert_to_activity_name(apk)

        start_sample(activity_name, gles_version)
        run_tests(activity_name, gles_version)
        wait_for_output(emulator, b'emulator: skin_winsys_destroy\r\n', 300)

    except Exception as error:
        print("Error while trying to test %s on %s : %s" % (os.path.split(apk)[-1], emulator_name, error))
        check_for_crashes()
        print('-' * 70)
        kill_emulator_process()
        wait_for_output(emulator, b'emulator: skin_winsys_destroy\r\n', 300)


if __name__ == '__main__':
    apk_files = get_sample_apks()

    for apk in apk_files:
        if 'CommonSampleApplication' in apk:
            continue
        for emulator_name in emulator_names:
            verify_android_apk(apk, emulator_name)
