import subprocess
import os

project_path = "/Users/daniel/Desktop/Projects/HMDataAugmentation/corpusHelper/minProgram"
clean_command = "hvigorw clean"
hap_command = "hvigorw assembleHap"
app_command = "hvigorw assembleApp"
test_command = "hvigorw test"

def run_command(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode('utf-8'), err.decode('utf-8')


if __name__ == '__main__':
    pwd_returncode, pwd_result, pwd_err = run_command("pwd")
    print("pwd_result: ", pwd_result)
    if pwd_returncode != 0:
        print("Error running pwd:", pwd_err)

    error_message = ""

    try:
        os.chdir(project_path)
    except Exception as e:
        print("Error changing directory:", e)

    clean_returncode, clean_result, clean_err = run_command(clean_command)
    if clean_returncode != 0:
        print("Error running clean command:", clean_err)
    print("clean command finished")

    hap_returncode, hap_result, hap_err = run_command(hap_command)
    if hap_returncode != 0:
        # print("Error running assembleHap command:", hap_err)
        error_message += hap_err
    print("assembleHap command finished")

    app_returncode, app_result, app_err = run_command(app_command)
    if app_returncode != 0:
        # print("Error running assembleApp command:", app_err)
        error_message += hap_err
    print("assembleApp command finished")

    if error_message:
        print("Error message: ", error_message)

    # todo: change /HMDataAugmentation/corpusHelper/minProgram/entry/src/test/LocalUnit.test.ets and /HMDataAugmentation/corpusHelper/minProgram/entry/src/main/ets/pages/Index.ets

