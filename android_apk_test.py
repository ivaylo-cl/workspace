import os
import subprocess
import time
import psutil

emulator_names = [
    'pixel_10.0',
    'pixel_9.0',
    'pixel_8.1',
    'pixel_7.1',
    'pixel_7.0',
    'pixel_6.0',
    'pixel_5.1',
]

gles_to_test = [
    'gles2',
    'gles3',
]

def kill_process():
    emulator = 'qemu-system-x86_64.exe'

    for process in psutil.process_iter():
        if process.name() == emulator:
            process.kill()


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
    print('Starting emulator')
    command = 'emulator -avd %s -wipe-data'
    return subprocess.Popen(command % emulator_name, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)


def test_android_apk():
    emulator_path = os.path.abspath(os.getenv('LOCALAPPDATA') + '/Android/Sdk/emulator/bin64')

    directory_path = os.path.dirname(emulator_path)
    os.chdir(directory_path)
    apk_path = os.path.abspath('Samples/build')
    files = []
    # r=root, d=directories, f=files
    for r, d, f in os.walk(apk_path):
        for file in f:
            if '.apk' in file:
                files.append(os.path.join(r, file))

    for f in files:
        for emulator_name in emulator_names:
            boot_device = b'emulator: INFO: boot completed\r\n'
            try:
                if '.apk' in f:
                    open_emulator = start_emulator(emulator_name)  # Generic_9.0 / Pixel_XL_9.0

                    wait_for_output(open_emulator, boot_device, 300)
                    print('Installing: ', f)

                    subprocess.check_output('adb install ' + f, shell=True)
                    print('Install success')
                    time.sleep(3)

                    for gles in gles_to_test:
                        subprocess.check_output('adb shell monkey -p com.coherentlabs.coherentsample.%s -v 500' % gles,
                                         shell=True)
                        time.sleep(2)

                        subprocess.Popen('adb shell pm clear com.coherentlabs.coherentsample.%s' % gles, shell=True)
                        print('Close apk')
                        time.sleep(2)

                        subprocess.check_output('adb uninstall com.coherentlabs.coherentsample.%s' % gles, shell=True)
                        print('Uninstall success')
                        time.sleep(3)
                        kill_process()
                        time.sleep(2)

            except Exception as e:
                print("Error while installing %s: %s" % (f, str(e)))
                kill_process()
                time.sleep(1)
                continue
test_android_apk()
