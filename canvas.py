"""Gets files from Canvas of Instructure"""

import argparse
import dataclasses
import os
import re

import colorama
import requests

colorama.init(autoreset=True)


def print_c(string, type_, padding, **kwarg):
    """Prints with color"""
    padded = " " * padding + string
    if type_ == "error":
        print(colorama.Fore.RED + padded, **kwarg)
    elif type_ == "new":
        print(colorama.Fore.GREEN + padded, **kwarg)
    elif type_ == "group":
        print(colorama.Fore.BLACK + colorama.Back.WHITE + padded, **kwarg)
    elif type_ == "existing":
        print(colorama.Fore.YELLOW + padded, **kwarg)
    elif type_ == "item":
        print(padded, **kwarg)


def get_external_download_url(url: str) -> bool:
    """
    This should return an URL where the file can be downloaded.
    Supported sites:
    - docs.google.com
    """

    # Try Google Drive
    exp = re.compile(r"https:\/\/drive\.google\.com\/file\/d\/(?P<id>[^/]*)/")
    result = exp.search(url)
    if result:
        document_id = result.group("id")
        return f"https://docs.google.com/uc?export=download&id={document_id}"

    return None


def get_file_name_by_header(header) -> str:
    """Tries to get the file name from the header"""
    if not header:
        return ""
    exp = re.compile(r"filename=\"(?P<file_name>[^\"]*)\"")
    exp_utf8 = re.compile(r"filename\*=UTF-8''(?P<file_name>[^\"]*)")
    result = exp.search(header)
    result_utf8 = exp_utf8.search(header)
    if result_utf8:
        return requests.utils.unquote(result_utf8.group("file_name"))
    if result:
        return requests.utils.unquote(result.group("file_name"))
    return ""


@dataclasses.dataclass
class CanvasApi:
    """Canvas REST API wrapper"""

    # Check https://canvas.instructure.com/doc/api/

    domain: str
    token: str
    out_dir: str

    def __url(self, query):
        return "/".join(("https:/", self.domain, "api/v1", query))

    def __get(self, query: str):
        response = requests.get(
            url=self.__url(query), headers={"Authorization": f"Bearer {self.token}"},
        )
        return response.json()

    def get_courses(self, only_favorites: bool = True) -> list:
        """Returns the enrolled courses"""
        if only_favorites:
            return self.__get("users/self/favorites/courses")
        return self.__get("courses")

    def get_folders(self, course_id: int) -> list:
        """Gets the folders of a course"""
        return self.__get(f"courses/{course_id}/folders")

    def get_modules(self, course_id: int) -> list:
        """Gets the modules of a course"""
        return self.__get(f"courses/{course_id}/modules")

    def get_files_from_folder(self, folder_id: int) -> list:
        """Gets the files of a folder"""
        return self.__get(f"folders/{folder_id}/files")

    def get_modules_items(self, course_id: int, module_id: int) -> list:
        """Gets the module items of a course"""
        return self.__get(f"courses/{course_id}/modules/{module_id}/items")

    def get_file_from_id(self, course_id: int, file_id: int) -> dict:
        """Gets a file of a specific course using it's id"""
        return self.__get(f"courses/{course_id}/files/{file_id}")

    # Special methods

    def download_files(self, all_courses=False, use="both"):
        """Downloads files from Canvas"""
        courses = self.get_courses(not all_courses)

        if "errors" in courses:
            print_c("error: " + courses["errors"][0]["message"], "error", 0)
            return False

        for course in courses:
            print_c(course["course_code"], type_="group", padding=0)
            course_code, course_id = course["id"], course["course_code"]

            methods = [self._download_from_modules, self._download_from_foldes]

            if use == "both":
                for method in methods:
                    method(course_code, course_id)
                continue

            if use == "folders":
                methods.reverse()

            avaible = methods[0](course_code, course_id)
            if not avaible:
                methods[1](course_code, course_id)
        return True

    def _download_from_foldes(self, course_id, course_name):
        folders_list = self.get_folders(course_id)
        for folder in folders_list:

            if not folder["files_count"]:
                continue

            files_list = self.get_files_from_folder(folder["id"])

            if "errors" in files_list:
                return False

            folder_path = [course_name] + folder["full_name"].split("/")[1:]
            print_c("[F] " + folder["full_name"], "item", 1)

            for file_obj in files_list:
                self._dowload_file(
                    file_obj["url"], folder_path, file_obj["display_name"]
                )

        return True

    def _download_from_modules(self, course_id, course_name):
        modules_list = self.get_modules(course_id)

        for module in modules_list:

            if not module["items_count"]:
                continue

            module_items = self.get_modules_items(course_id, module["id"])

            if "errors" in module_items:
                return False

            folder_path = [course_name, module["name"].strip()]
            print_c("[M] " + module["name"], "item", 1)

            for item in module_items:
                if item["type"] == "File":
                    file_obj = self.get_file_from_id(course_id, item["content_id"])
                    self._dowload_file(
                        file_obj["url"], folder_path, file_obj["display_name"]
                    )
                elif item["type"] == "ExternalUrl":
                    external_url = get_external_download_url(item["external_url"])
                    if external_url:
                        file_url = external_url
                        self._dowload_file(file_url, folder_path)
        return True

    def _dowload_file(self, file_url, folder_path, name=""):
        """Downloads a file object"""
        dir_path = os.path.join(self.out_dir, *folder_path)

        # See if the directory is valid
        try:
            os.makedirs(os.path.join(dir_path), exist_ok=True)
        except NotADirectoryError:
            print_c("error: invalid path", type_="error", padding=2)

        if name:  # if a name in given
            # Check the file name
            file_name = name
            # Checks if the file exists
            file_path = os.path.join(self.out_dir, *folder_path, file_name)
            if os.path.exists(file_path):
                print_c(file_name, type_="existing", padding=2)
                return
            # Starts the request if it doesn't
            download_response = requests.get(file_url, stream=True)
        else:
            # Starts the request
            download_response = requests.get(file_url, stream=True)
            content_header = download_response.headers.get("Content-Disposition")
            # Check the file name
            if not content_header:
                return
            file_name = get_file_name_by_header(content_header)
            if not file_name:
                return
            # Checks if the file exists
            file_path = os.path.join(self.out_dir, *folder_path, file_name)
            if os.path.exists(file_path):
                print_c(file_name, type_="existing", padding=2)
                return

        content_len = download_response.headers.get("content-length", None)

        # Download file
        print_c(" | ".join((f"{0:3.0f}%", file_name,)), "new", 2, end="\r")
        with open(file_path, "wb") as file:
            if not content_len:
                print_c(" | ".join(("???%", file_name,)), "new", 2)
                file.write(download_response.content)
                return

            progress = 0
            total_len = int(content_len)

            for data in download_response.iter_content(chunk_size=4096):
                file.write(data)
                progress += len(data)
                perc = (progress / total_len) * 100
                print_c(" | ".join((f"{perc:3.0f}%", file_name,)), "new", 2, end="\r")
            print(end="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files from Canvas")
    parser.add_argument("token", metavar="TOKEN", help="Canvas access token")
    parser.add_argument("domain", metavar="DOMAIN", help="Canvas domain")
    parser.add_argument(
        "from_where",
        metavar="FROM",
        help="Download from modules, folders or both (Default: both)",
        choices=("modules", "folders", "both"),
    )
    parser.add_argument(
        "--all", action="store_true", help="Get all courses instead of only favorites"
    )
    parser.add_argument("out_dir", metavar="OUT_DIR", help="Out directory")

    args = parser.parse_args()

    API = CanvasApi(args.domain, args.token, args.out_dir)
    API.download_files(args.all, args.from_where)
