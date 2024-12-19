import subprocess
import os

project_path = "/Users/daniel/Desktop/Projects/HMDataAugmentation/corpusHelper/minProgram"
clean_command = "hvigorw clean"
hap_command = "hvigorw assembleHap"
app_command = "hvigorw assembleApp"

def run_command(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode('utf-8'), err.decode('utf-8')

if __name__ == '__main__':
    pwd_returncode, pwd_result, pwd_err = run_command("pwd")
    print("pwd_result: ", pwd_result)
    if pwd_returncode != 0:
        print("Error running pwd:", pwd_err)

    try:
        os.chdir(project_path)
    except Exception as e:
        print("Error changing directory:", e)

    clean_returncode, clean_result, clean_err = run_command(clean_command)
    if clean_returncode != 0:
        print("Error running clean command:", clean_err)

    hap_returncode, hap_result, hap_err = run_command(hap_command)
    if hap_returncode != 0:
        print("Error running assembleHap command:", hap_err)

    app_returncode, app_result, app_err = run_command(app_command)
    if app_returncode != 0:
        print("Error running assembleApp command:", app_err)

    print("clean_result: ", clean_result)
    print("hap_result: ", hap_result)
    print("app_result: ", app_result)