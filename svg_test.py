import os
import sys
import subprocess
import time
from datetime import date

def create_file_log():
    return "SVG-Log-" + str(date.today()) + " " + str(time.strftime("%H-%M-%S")) + ".txt"

name = create_file_log()
print("NAME", name)

path = 'D:\\Work\\PyTests\\Logs\\ ' + name
print("PATH", path)

def run_player():
    global player
    player = 'D:\\Work\\Gameface-0.0.0.0-Pro\\Player\\Player.exe '

def run_test():

    sys.stdout = open('D:\\Work\\PyTests\\Logs\\ ' + name, "w", encoding="utf-8")
    file_path = os.path.abspath('D:\\SVG_test\\cohtml-html')
    path = os.path.abspath('D:/')

    for file in os.listdir(file_path):
        if os.path.isfile(os.path.join(file_path, file)):
            url = ('coui://SVG_test/cohtml-html/' + file)
            time.sleep(1)
            print(str(file))
            svg_test = subprocess.Popen([player, '--root', path, '--url', url])
            time.sleep(4)
# no need for now - # ['utf-8', 'utf-16', 'utf-32', 'utf-16-be', 'utf-16-le', 'utf-32-be', 'utf-32-le', 'us-ascii']:
            for format in ['utf-8', 'utf-16']:
                try:
                    file_logs = open('TestApp.log', encoding=format)
                    lines = file_logs.read()
                    print(str(lines))
                    file_logs.close()
                    break
                except Exception as e:
                    print(e)
                    continue
            time.sleep(2)
            print("================================================================")
            if svg_test.poll() is None:
                svg_test.kill()
            else:
                print('Warning: Crash:', svg_test.poll())
                print("================================================================")
                time.sleep(1)

# check player process
def get_tasks(Player):

    get_all_process = os.popen('tasklist /v').read().strip().split('\n')
    pass

    for i in range(len(get_all_process)):
        s = get_all_process[i]
        if Player in get_all_process[i]:
            return get_all_process[i]
    return []

if __name__ == '__main__':


    img_player = 'Player.exe'

    notResponding = 'Not Responding'

    get_all_process = get_tasks(img_player)

    if not get_all_process:
        print('%s - No such process... Player starting' % (img_player))

    elif 'Not Responding' in get_all_process:
        print('%s is Not responding' % (img_player))

    else:
        print('%s is Running' % (img_player))
        pass

    get_tasks('Player')

    create_file_log()
    run_player()
    run_test()











