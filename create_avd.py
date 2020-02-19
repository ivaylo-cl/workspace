import subprocess

android_systems = {
    'android-22': 'pixel_5.1',
    'android-23': 'pixel_6.0',
    'android-24': 'pixel_7.0',
    'android-25': 'pixel_7.1',
    'android-26': 'pixel_8.0',
    'android-28': 'pixel_9.0',
    'android-29': 'pixel_10.0',
}

def install_system():
    for system in android_systems.keys():
        print('Installing %s' % system)
        command = 'sdkmanager --install "system-images;%s;google_apis;x86_64'
        subprocess.check_output(command % system, shell=True)
        # subprocess.check_output('sdkmanager --licenses', shell=True) Licenses should be accepted!

def create_avd():
    for android_version, android_device in android_systems.items():
        print('Creating %s' % android_device)
        subprocess.check_output('avdmanager create avd --name "{0}" --package "system-images;{1};google_apis;x86_64" '
                                '--device "Nexus" --tag "google_apis" '
                                '--abi "x86_64"'.format(android_device, android_version), shell=True)
        print('Done')

install_system()
create_avd()
