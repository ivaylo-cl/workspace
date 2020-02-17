import os
import subprocess
import time
import psutil

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
    print('Starting emulator')
    command = 'emulator -avd %s -wipe-data'
    return subprocess.Popen(command % emulator_name, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)


def test_android_apk():
    emulator_path = os.path.abspath('C:\\Users\\ivaylo.nichaev\\AppData\\Local\\Android\\Sdk\\emulator\\bin64')
    directory_path = os.path.dirname(emulator_path)
    os.chdir(directory_path)
    apk_path = os.path.abspath('C:\\Gameface-0.0.0.0-builds\\Gameface-0.0.0.0-Pro-Samples-Android\\Android')
    files = []
    # r=root, d=directories, f=files
    for r, d, f in os.walk(apk_path):
        for file in f:
            if '.apk' in file:
                files.append(os.path.join(r, file))

    for f in files:
        boot_device = b'emulator: INFO: boot completed\r\n'
        try:
            if 'GLES2.apk' in f:
                open_emulator = start_emulator('Pixel_XL_9.0')

                wait_for_output(open_emulator, boot_device, 300)
                print('Installing: ', f)

                subprocess.check_output("adb install " + f, shell=True)
                print('Install success')
                time.sleep(3)

                subprocess.check_output('adb shell monkey -p com.coherentlabs.coherentsample.gles2 -v 500',
                                 shell=True)
                time.sleep(2)

                subprocess.Popen('adb shell pm clear com.coherentlabs.coherentsample.gles2', shell=True)
                print('Close apk')
                time.sleep(2)

                subprocess.check_output('adb uninstall com.coherentlabs.coherentsample.gles2', shell=True)
                print('Uninstall success')
                time.sleep(3)
                kill_process()
                time.sleep(2)

                # subprocess.Popen('emulator -avd Pixel_XL_9.0 -wipe-data', shell=True)
                # time.sleep(2)
                # kill_process()
                # time.sleep(1)

            if 'GLES3.apk' in f:
                open_emulator2 = start_emulator('Pixel_3_XL_9.0')

                wait_for_output(open_emulator2, boot_device, 300)
                print('Installing: ', f)

                subprocess.check_output('adb install ' + f)
                print('Install success')
                time.sleep(3)

                subprocess.Popen('adb shell monkey -p com.coherentlabs.coherentsample.gles3 -v 500',
                                 shell=True)
                time.sleep(2)

                subprocess.Popen('adb shell pm clear com.coherentlabs.coherentsample.gles3', shell=True)
                print('Close apk')
                time.sleep(2)

                subprocess.Popen('adb uninstall com.coherentlabs.coherentsample.gles3', shell=True)
                time.sleep(3)
                kill_process()
                time.sleep(2)

                # subprocess.Popen('emulator -avd Pixel_3_XL_9.0 -wipe-data', shell=True)
                # kill_process()
                # time.sleep(3)

        except Exception as e:
            print("Error while installing %s: %s" % (f, str(e)))
            kill_process()
            time.sleep(1)
            continue
test_android_apk()