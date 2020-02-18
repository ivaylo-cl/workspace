import subprocess

android_systems = [
    'android-22',
    'android-23',
    'android-24',
    'android-25',
    'android-27',
    'android-28',
    'android-29'
]

device_names = [
    'pixel_5.1',
    'pixel_6.0',
    'pixel_7.0',
    'pixel_7.1',
    'pixel_8.1',
    'pixel_9.0',
    'pixel_10.0'
]

def install_system():
    for system in android_systems:
        print('Installing %s' % system)
        command = 'sdkmanager --install "system-images;%s;google_apis;x86_64'
        subprocess.check_output(command % system, shell=True)

def create_avd():
    for avd_names in device_names:
        print('Creating %s' % avd_names)
        subprocess.check_output('echo "no" | avdmanager --verbose create avd --force --name "{0}" '
                                '--device "pixel"--package "system-images;{1};google_apis;x86_64"'
                                ' --tag "google_apis" --abi "x86_64"'.format(avd_names, android_systems), shell=True)
        print('Done')

install_system()
create_avd()