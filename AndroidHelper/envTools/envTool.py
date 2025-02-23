import platform
import subprocess
import os

JDKs_root = '/Users/daniel/Library/Java/JavaVirtualMachines/'

def get_system_type():
    system = platform.system()
    if system == 'Darwin':
        return 'Mac'
    elif system == 'Windows':
        return 'Windows'
    elif system == 'Linux':
        return 'Linux'
    else:
        return 'Unknown'


def change_jdk_version(version):
    system_type = get_system_type()
    try:
        if system_type == 'Mac':
            java_home = subprocess.check_output(['/usr/libexec/java_home', '-v', version]).strip().decode('utf-8')
            with open(os.path.expanduser('~/.zshrc'), 'a') as file:
                file.write(f'\nexport JAVA_HOME={java_home}\nexport PATH=$JAVA_HOME/bin:$PATH\n')
            subprocess.run(['source', os.path.expanduser('~/.zshrc')], shell=True, check=True)
        elif system_type == 'Windows':
            subprocess.run(['setx', 'JAVA_HOME', f'C:\\Program Files\\Java\\jdk{version}'], check=True)
            subprocess.run(['setx', 'Path', '%Path%;%JAVA_HOME%\\bin'], check=True)
        elif system_type == 'Linux':
            java_home = f'/usr/lib/jvm/java-{version}-openjdk-amd64'
            with open(os.path.expanduser('~/.bashrc'), 'a') as file:
                file.write(f'\nexport JAVA_HOME={java_home}\nexport PATH=$JAVA_HOME/bin:$PATH\n')
            subprocess.run(['source', os.path.expanduser('~/.bashrc')], shell=True, check=True)
        else:
            print("Unsupported system type.")
    except subprocess.CalledProcessError as e:
        print(f"Error changing JDK version: {e}")


if __name__ == "__main__":
    jdk_version = input("Enter the JDK version you want to switch to (e.g., 11, 8): ")
    change_jdk_version(jdk_version)