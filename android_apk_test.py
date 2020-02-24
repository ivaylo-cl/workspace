import os
import subprocess
import time
import psutil


emulator_names = [
    'pixel_10.0',
    'pixel_9.0',
    # 'pixel_8.0',
    # 'pixel_7.1',
    # 'pixel_7.0',
    # 'pixel_6.0',
    # 'pixel_5.1',
]


gles_to_test = [
    'gles2',
    'gles3',
]


activity = [
    'SampleHelloCohtmlActivity',
    'SampleNameplatesActivity',
]


def kill_process():
    emulator = 'qemu-system-x86_64.exe'

    for process in psutil.process_iter():
        if process.name() == emulator:
            process.kill()


def hello_cohtml_test():
    hello_cohtml = subprocess.check_output('python cohtml/Samples/Tests/SampleHelloCohtml.py', shell=True)
    print(hello_cohtml)


def nameplates_test():
    nameplates = subprocess.check_output('python cohtml/Samples/Tests/SampleNameplates.py', shell=True)
    print(nameplates)


def wait_for_output(open_emulator, expected_output, seconds_to_wait):
    starting_time = time.time()
    for line in iter(open_emulator.stdout.readline, ''):
        if line == expected_output:
            elapsed_seconds = time.time() - starting_time
            if elapsed_seconds > seconds_to_wait:
                raise Exception("Waited more than %d seconds for output %s" % (seconds_to_wait, expected_output))
            break
        else:
            print(">>> " + str(line.rstrip()))


def start_emulator(emulator_name):
    ''' Starts an emulator and returns a reference to it, given its name'''

    emulator_path = os.path.abspath('C:/Android/Sdk/emulator/bin64')
    directory_path = os.path.dirname(emulator_path)
    os.chdir(directory_path)
    print('Starting emulator:', emulator_name)
    command = 'emulator -avd %s -wipe-data'
    return subprocess.Popen(command % emulator_name, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)


def start_and_test_app(gles, activity):
    '''start app, forward port and run tests'''

    run_app = subprocess.check_output('adb shell am start -n com.coherentlabs.coherentsample.%s/'
                            'com.coherentlabs.coherentsample.%s' % (gles, activity), shell=True)
    print(run_app)
    subprocess.check_output('adb forward tcp:9444 tcp:9444')
    time.sleep(4)

    if b'Starting: Intent { cmp=com.coherentlabs.coherentsample.gles2' \
       b'/com.coherentlabs.coherentsample.SampleHelloCohtmlActivity }\r\n' or \
       b'Starting: Intent { cmp=com.coherentlabs.coherentsample.gles3' \
       b'/com.coherentlabs.coherentsample.SampleHelloCohtmlActivity }\r\n' in run_app:
        hello_cohtml_test()
    else:
        nameplates_test()

    time.sleep(2)

    subprocess.check_output('adb shell pm clear com.coherentlabs.coherentsample.%s' % gles, shell=True)
    print('Close apk')
    time.sleep(1)

    subprocess.check_output('adb uninstall com.coherentlabs.coherentsample.%s' % gles, shell=True)
    print('Uninstall success')
    print('-'*70)
    time.sleep(2)
    kill_process()


def install_apk():
    '''r = root, d = directory, f = file'''

    apk_path = os.path.abspath('cohtml/NativeSamples/Unpacked/Samples/Android/')
    files = []
    for r, d, f in os.walk(apk_path):
        for file in f:
            if '.apk' in file:
                files.append(os.path.join(r, file))

    for f in files:
        for emulator_name in emulator_names:
            boot_device = b'emulator: INFO: boot completed\r\n'
            try:
                if '.apk' in f:
                    open_emulator = start_emulator(emulator_name)

                    wait_for_output(open_emulator, boot_device, 300)
                    print('Installing: ', f)

                    subprocess.check_output('adb install ' + f, shell=True)
                    print('Install success')
                    time.sleep(2)
                    if 'SampleHelloCohtml-GLES2' in f:
                        start_and_test_app('gles2', 'SampleHelloCohtmlActivity')
                        continue
                    if 'SampleHelloCohtml-GLES3' in f:
                        start_and_test_app('gles3', 'SampleHelloCohtmlActivity')
                        continue
                    if 'SampleNameplates-GLES2' in f:
                        start_and_test_app('gles2', 'SampleNameplatesActivity')
                        continue
                    if 'SampleNameplates-GLES3' in f:
                        start_and_test_app('gles3', 'SampleNameplatesActivity')
                        continue


            except Exception as e:
                print("Error while installing %s: %s" % (f, str(e)))
                kill_process()
                time.sleep(1)
                continue
install_apk()
