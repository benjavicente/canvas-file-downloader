"""Gets files from Canvas of Instructure"""

import argparse
import dataclasses
import os
import sys

import requests

import colorama

colorama.init(autoreset=True)


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
        if only_favorites:
            return self.__get("users/self/favorites/courses")
        return self.__get("courses")

    def get_folders(self, course_id: int) -> list:
        """Gets the folders of a course"""
        return self.__get(f"courses/{course_id}/folders")

    def get_files_from_folder(self, folder_id: int) -> list:
        """Gets the files of a folder"""
        return self.__get(f"folders/{folder_id}/files")


def main(token, url, all_courses):
    """Gets files from Canvas of Instructure"""
    canvas_api = CanvasApi(url, token)

    courses = canvas_api.get_courses(not all_courses)

    if "errors" in courses:
        raise KeyError("Invalid Token")

    for course in courses:
        print(
            f"\n{colorama.Back.WHITE}{colorama.Fore.BLACK}"
            f"{course['course_code']}: {course['name']}"
        )

        for folder in canvas_api.get_folders(course["id"]):

            # If a folder doesn't have files, it's skipped
            if not folder["files_count"]:
                continue

            print(f"  - {folder['full_name']}")

            files_response = canvas_api.get_files_from_folder(folder["id"])

            if "errors" in files_response:
                print(
                    f"{colorama.Fore.RED}      " f"! error: {files_response['status']}"
                )
                continue

            # Path of the local folder
            folder_path = [
                "out",
                course["course_code"],
                *folder["full_name"].split("/")[1:],
            ]

            try:
                os.makedirs(os.path.join(*folder_path), exist_ok=True)
            except NotADirectoryError:
                # TODO: handle invalid directory names
                print(f"{colorama.Fore.RED}      " f"! error: invalid directory name")
                continue

            for folder_file in files_response:

                file_path = os.path.join(*folder_path, folder_file["display_name"])

                # If the folder exists, it's printed in yellow and marked with *
                if os.path.exists(file_path):
                    print(
                        f"{colorama.Fore.YELLOW}      "
                        f"* {folder_file['display_name']}"
                    )
                    continue

                # If it doesn't exists, starts to download it
                file_name = folder_file["display_name"]

                print(f"{colorama.Fore.GREEN}     + {0.:3.0f}% | {file_name}", end="\r")

                response = requests.get(folder_file["url"], stream=True)
                length = response.headers.get("content-length")

                before = -1
                progress = 0
                with open(file_path, "wb") as file:

                    if length:
                        total_length = int(length)
                    else:
                        file.write(response.content)
                        print(
                            f"{colorama.Fore.GREEN}     + ???% | {file_name}", end="\r"
                        )
                        break

                    for data in response.iter_content(chunk_size=4096):
                        progress += len(data)
                        file.write(data)
                        now = (progress / total_length) * 100
                        if before < now:
                            before = now
                            print(
                                f"{colorama.Fore.GREEN}     + {now:3.0f}% | {file_name}",
                                end="\r",
                            )
                print(end="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files from Canvas")
    parser.add_argument("token", metavar="TOKEN", help="Canvas access token")
    parser.add_argument("url", metavar="URL", help="Canvas domain")
    parser.add_argument(
        "--all", action="store_true", help="Get all courses instead of only favorites"
    )
    args = parser.parse_args()
    main(args.token, args.url, args.all)
