import os
import subprocess
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


def kill_emulator_process(emulator):
    subprocess.check_output('adb emu kill', shell=True)
    wait_until_emulator_dies(emulator, 300)


def start_emulator(emulator_name):
    ''' Starts an emulator and returns a reference to it, given its name.'''

    os.environ.get('ANDROID_SDK_ROOT')
    print('Starting emulator:', emulator_name)
    command = 'emulator -avd %s -wipe-data'

    emulator = subprocess.Popen(command % emulator_name,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.STDOUT,
                                shell=True)
    return emulator


def wait_until_emulator_dies(emulator, seconds_to_wait):
    starting_time = time.time()

    result = None
    while result is None:
        try:
            result = emulator.wait(2)
        except subprocess.TimeoutExpired:
            pass
    print('Emulator terminated')
    print('=' * 70)

    elapsed_seconds = time.time() - starting_time
    if elapsed_seconds > seconds_to_wait:
        emulator.kill()
        raise Exception("Waited more than %d seconds to terminate %s"
                        % (seconds_to_wait, emulator_name))


def wait_for_boot_completed(seconds_to_wait):
    starting_time = time.time()

    # The emulator must return 15 times b'stopped' so we understand
    # that the device has started before start installing akp.
    # The 'check_for_animation_end' constant needed,
    # because android 9 return stopped when changing the loading animation.

    device_status = b''
    check_for_animation_end = 15
    count = check_for_animation_end
    while count != 0:
        try:
            device_status = subprocess.check_output('adb shell getprop init.svc.bootanim',
                                                    stderr=subprocess.DEVNULL)
            device_status = device_status.rstrip()
            if device_status == b'stopped':
                count -= 1
            else:
                count = 15

        except subprocess.CalledProcessError as e:
            pass

        elapsed_seconds = time.time() - starting_time
        if elapsed_seconds > seconds_to_wait:
            raise Exception("Waited more than %d seconds to load android %s"
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
        raise Exception('Only apps with GLES2 backend are supported. '
                        'App: %s' % os.path.split(apk_name)[-1])

    return backend_version


def run_hello_cohtml_test():
    print('Starting SampleHelloCohtml tests')
    subprocess.check_output('python  cohtml/Samples'
                            '/Tests/SampleHelloCohtml.py',
                            shell=True)


def run_nameplates_test():
    print('Starting SampleNameplates tests')
    subprocess.check_output('python cohtml/Samples'
                            '/Tests/SampleNameplates.py',
                            shell=True)


def close_app(gles_version):
    print(os.path.split(apk)[-1], 'tests have been completed!')
    subprocess.check_output('adb shell pm clear '
                            'com.coherentlabs.coherentsample.%s'
                            % gles_version, shell=True)
    print('App closed')


def uninstall_app(gles_version, emulator):
    subprocess.check_output('adb uninstall '
                            'com.coherentlabs.coherentsample.%s'
                            % gles_version, shell=True)
    print('Uninstall successful')
    kill_emulator_process(emulator)


def start_sample(activity_name, gles_version):
    '''Starts an app, forwards the port and runs tests.
    When test are done, closes and uninstalls the app.'''

    print('Starting аpp')
    subprocess.check_output('adb shell am start -n '
                            'com.coherentlabs.coherentsample.%s/'
                            'com.coherentlabs.coherentsample.%s'
                            % (gles_version, activity_name), shell=True)

    subprocess.check_output('adb forward tcp:9444 tcp:9444')


def check_for_crashes():
    print('Crash has been found!')
    check = subprocess.check_output('adb logcat -b crash --regex DEBUG '
                                    '--max-count 100 --print -d', shell=True)

    for new_line in check.split(b'\n'):
        print('%r' % new_line)

def check_for_crashes_android_6():
    print('Crash has been found!')
    check = subprocess.check_output('adb logcat -b crash -d', shell=True)

    for new_line in check.split(b'\n'):
        print('%r' % new_line)


def run_tests(activity_name, gles_version, emulator):
    if activity_name == 'SampleHelloCohtmlActivity':
        run_hello_cohtml_test()
    elif activity_name == 'SampleNameplatesActivity':
        run_nameplates_test()
    else:
        raise Exception('Unknown sample:', activity_name)

    close_app(gles_version)
    uninstall_app(gles_version, emulator)


def install_apk(apk_name):
        print('Installing:', os.path.split(apk_name)[-1])
        subprocess.check_call('adb install ' + apk_name, shell=True)
        print('Install successful')


def verify_android_apk(apk, emulator_name):
    '''Opens an emulator and waiting to boot completed,
    then gets the GLES version and installs an apk.
    Gives information about app backend and activity to start tests.'''


    emulator = start_emulator(emulator_name)

    try:
        wait_for_boot_completed(300)
        install_apk(apk)

        gles_version = get_gles_version(apk)
        activity_name = convert_to_activity_name(apk)

        start_sample(activity_name, gles_version)
        run_tests(activity_name, gles_version, emulator)

    except Exception as error:
        print("Error while trying to test %s on %s : %s"
              % (os.path.split(apk)[-1], emulator_name, error))

        if emulator_name != 'pixel_6.0':
            check_for_crashes()
        else:
            check_for_crashes_android_6()
        print(os.path.split(apk)[-1], 'tests ended')
        kill_emulator_process(emulator)


if __name__ == '__main__':
    apk_files = get_sample_apks()

    #  GLES3 crashes when trying to load,
    #  should be fixed before added in tests.
    #  GLES3 works on mobile devices.

    for apk in apk_files:
        if 'CommonSampleApplication' in apk:
            continue
        elif 'gles3' in apk:
            continue
        for emulator_name in emulator_names:
            verify_android_apk(apk, emulator_name)
