"""Gets files from Canvas of Instructure"""

import dataclasses
import os
import sys

import requests


@dataclasses.dataclass
class CanvasApi:
    """Canvas REST API wrapper"""

    # Check https://canvas.instructure.com/doc/api/

    domain: str
    token: str

    def __url(self, query):
        return "/".join(("https:/", self.domain, "api/v1", query))

    def __get(self, query: str):
        response = requests.get(
            url=self.__url(query), headers={"Authorization": f"Bearer {self.token}"},
        )
        return response.json()

    def get_courses(self, only_favorites: bool = True) -> list:
        """Returns the enrolled courses"""
        # https://canvas.instructure.com/doc/api/favorites.html
        # https://canvas.instructure.com/doc/api/courses.html#method.courses.user_index
        if only_favorites:
            return self.__get("users/self/favorites/courses")
        return self.__get("courses")

    def get_folders(self, course_id: int) -> list:
        """Gets the folders of a course"""
        # https://canvas.instructure.com/doc/api/files.html#method.folders.list_all_folders
        return self.__get(f"courses/{course_id}/folders")

    def get_files_from_folder(self, folder_id: int) -> list:
        """Gets the files of a folder"""
        # https://canvas.instructure.com/doc/api/files.html#method.files.api_index
        return self.__get(f"folders/{folder_id}/files")


def main(token):
    """Gets files from Canvas of Instructure"""
    canvas_api = CanvasApi("cursos.canvas.uc.cl", token)

    courses = canvas_api.get_courses()

    if "errors" in courses:
        raise KeyError("Invalid Token")

    for course in courses:
        print(course["course_code"], course["name"])

        for folder in canvas_api.get_folders(course["id"]):

            print(" " * 4 + folder["full_name"])

            files_response = canvas_api.get_files_from_folder(folder["id"])

            if "errors" in files_response:
                print(" " * 3 + "!error:", files_response["status"])
                continue

            folder_path = ["out", course["course_code"], *folder["full_name"].split("/")[1:]]
            os.makedirs(os.path.join(*folder_path), exist_ok=True)

            for folder_file in files_response:

                file_path = os.path.join(*folder_path, folder_file["display_name"])

                if os.path.exists(file_path):
                    print(" " * 6 + "* " + folder_file["display_name"])
                    continue

                print(" " * 8 + folder_file["display_name"])

                file_content = requests.get(folder_file["url"]).content

                with open(file_path, "wb") as file:
                    file.write(file_content)


if __name__ == "__main__":
    # https://cursos.canvas.uc.cl/profile/settings#access_tokens

    TOKEN = ":)"  # You can save your token here

    if len(sys.argv) == 2:
        TOKEN = sys.argv[1]

    main(TOKEN)
