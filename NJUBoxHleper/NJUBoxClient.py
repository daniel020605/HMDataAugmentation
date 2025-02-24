import urllib.parse
from pathlib import Path
import requests
class NJUBoxClient:
    def __init__(self,uname,password,appname):
        self.appname = appname
        url = "https://box.nju.edu.cn/api2/auth-token/"
        payload = {
            "username": uname,
            "password": password
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            self.token = response.json()["token"]
        else:
            raise Exception("鉴权失败!\n"+response.text)

    def getDefaultRepo(self):
        url = "https://box.nju.edu.cn/api2/default-repo/"
        headers = {
            "accept": "application/json",
            "authorization": "Token "+self.token
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            exists = response.json()["exists"]
            if exists:
                return response.json()["repo_id"]
            else:
                raise Exception("Repo Not Found")
        else:
            raise Exception("拉取仓库信息失败\n" + response.text)

    def downloadFile(self, repo_id, file_path, download_to):
        url = "https://box.nju.edu.cn/api2/repos/"+repo_id+"/file/?p="+urllib.parse.quote(file_path)
        headers = {
            "accept": "application/json",
            "authorization": "Token "+self.token
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            fileURL = response.text.strip('\"')
            if download_to!="JUSTURL":
                urllib.request.urlretrieve(fileURL, download_to)
            else:
                return fileURL
        else:
            raise Exception(response.text)

    def getUploadLink(self, repo_id, p):
        url = f"https://box.nju.edu.cn/api2/repos/{repo_id}/upload-link/?p={urllib.parse.quote(p)}"

        headers = {
            "accept": "application/json",
            "authorization": "Token "+self.token
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            uploadURL = response.text.strip('\"')
            return uploadURL
        else:
            raise Exception(response.text)

    def getUpdateLink(self,repo_id,p):
        url = f"https://box.nju.edu.cn/api2/repos/{repo_id}/update-link/?p={urllib.parse.quote(p)}"
        headers = {
            "accept": "application/json",
            "Authorization": "Token "+self.token
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            uploadURL = response.text.strip('\"')
            return uploadURL
        else:
            raise Exception(response.text)

    def updateFile(self,repo_id,file,target):
        url = self.getUpdateLink(repo_id,Path(target).parent.name)
        files = {"file": (Path(file).name, open(file, 'rb'))}
        payload = {"target_file": target}
        headers = {
            "accept": "application/json",
            "authorization": "Token "+self.token
        }
        response = requests.post(url, data=payload, files=files, headers=headers)
        if response.status_code == 200:
            return response
        else:
            raise Exception(response.text)

    def uploadFile(self,file_path,repo_id,parent_dir,relative_directory,replace=""):
        url = self.getUploadLink(repo_id,parent_dir)
        if replace!="":
            files = {"file": (
                urllib.parse.quote(Path(file_path).name), open(file_path, "rb"), "application/octet-stream"),
                "parent_dir": parent_dir,
                "relative_path": relative_directory,
                "replace":replace
            }
            headers = {
                "accept": "application/json",
                "authorization": "Token " + self.token
            }
        else:
            files = {"file": (
            urllib.parse.quote(Path(file_path).name), open(file_path, "rb"), "application/octet-stream"),
                "parent_dir": parent_dir,
                "relative_path":relative_directory
            }
            headers = {
                "accept": "application/json",
                "authorization": "Token "+self.token
            }
        response = requests.post(url, files=files, headers=headers)
        if response.status_code == 200:
            return response.text
        raise Exception(response.text)



    def createShareLink(self, repo_id, path,expire_days="",password="",can_edit=True,can_download=True,can_upload=True):
        url = "https://box.nju.edu.cn/api/v2.1/share-links/"
        if password == "":
            if expire_days == "":
                payload = {
                    "permissions": {
                        "can_edit": can_edit,
                        "can_download": can_download,
                        "can_upload": can_upload
                    },
                    "repo_id": repo_id,
                    "path": path
                }
            else:
                payload = {
                    "permissions": {
                        "can_edit": can_edit,
                        "can_download": can_download,
                        "can_upload": can_upload
                    },
                    "repo_id": repo_id,
                    "path": path,
                    "expire_days": expire_days
                }
        else:
            if expire_days != "":
                payload = {
                    "permissions": {
                        "can_edit": can_edit,
                        "can_download": can_download,
                        "can_upload": can_upload
                    },
                    "repo_id": repo_id,
                    "path": path,
                    "password": password,
                    "expire_days": expire_days
                }
            else:
                payload = {
                    "permissions": {
                        "can_edit": can_edit,
                        "can_download": can_download,
                        "can_upload": can_upload
                    },
                    "repo_id": repo_id,
                    "path": path,
                    "password": password,
                }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Token "+self.token
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code==200:
            return response.json()["link"]
        else:
            raise Exception(response.text)

    def allShareLinks(self):
        url = "https://box.nju.edu.cn/api/v2.1/share-links/"
        headers = {
            "accept": "application/json",
            "authorization": "Token "+self.token
        }
        response = requests.get(url, headers=headers)
        if response.status_code==200:
            return response.json()
        else:
            raise Exception(response.text)