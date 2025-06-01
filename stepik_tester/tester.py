from io import StringIO
from pathlib import Path
from time import sleep
import sys
import shutil
import os

from loguru import logger
import pyclip
import requests

from rich import pretty, print as rich_print


class BeeTester:
    def __init__(self, work_dir_path: str = "Test_for_Stepik") -> None:
        self._recv = None
        self._temp_directory_path = None
        self._temp_zip_path = None
        self._work_dir_path: Path = Path(work_dir_path)

    def download_lesson_archive(self, archive_url: str, func=None) -> None:
        self._work_dir_path.mkdir(exist_ok=True)
        self._temp_zip_path: Path = self._work_dir_path / Path(archive_url).name
        if not archive_url.startswith("http"):
            logger.error("\nIncorrect archive URL:\n %...", archive_url[:60])
            sys.exit(-1)
        try:
            self._recv = requests.get(archive_url, timeout=10)
            self._recv.raise_for_status()
            self._temp_zip_path.write_bytes(self._recv.content)

        except requests.RequestException:
            logger.error(
                "There was a problem with the request, check "
                "the URL or your internet connection:\n {}...".format(archive_url[:60])
            )
            sys.exit(-1)

    def unpacking(self, archive_url: str) -> None:
        self._temp_directory_path: Path = self._work_dir_path / Path(archive_url).stem

        if Path(archive_url).stem not in self._work_dir_path.iterdir():
            self._temp_directory_path: Path = (
                self._work_dir_path / Path(archive_url).stem
            )
            self._temp_directory_path.mkdir(exist_ok=True)
            logger.info(" Created temporary directory and starting unpacking")
            shutil.unpack_archive(self._temp_zip_path, self._temp_directory_path)
            logger.info("Zip archive unpacked")

        else:
            logger.warning("Temporary directory already exists")

    def checking_assignments(self) -> None:
        logger.info("Starting testing tasks")
        sleep(0.1)
        files = iter(
            sorted(self._temp_directory_path.iterdir(), key=lambda x: int(x.stem))
        )

        self.incorrect_solutions = 0
        try:
            while task_file := next(files, 0):
                answer: Path = next(files)
                with (
                    task_file.open("r", encoding="utf-8") as task_file,
                    answer.open("r", encoding="utf-8") as answer_file,
                ):
                    task = task_file.read()
                    ans = answer_file.read().split("\n")

                    buffer = StringIO()
                    sys.stdout = buffer
                    try:
                        exec(task)
                    except Exception as ex:
                        print(ex)
                    sys.stdout = sys.__stdout__

                    task_outputs: list[str] = buffer.getvalue().split("\n")

                    mismatched_lines: list[str] = []

                    for (string_num, right_answers), output in zip(
                        enumerate(ans, 1), task_outputs
                    ):
                        if right_answers != output:
                            mismatched_lines.append(
                                f"string № {string_num:} {right_answers:50}  {output}"
                            )

                    if mismatched_lines:
                        self.incorrect_solutions += 1
                        rich_print(
                            f"[bold red]Problem {Path(task_file.name).stem}[/bold red] failed\n\n"
                            f"[cyan][/cyan]"
                            f"{task}\n\n"
                            f"[red]Mismatched_lines:[/red]\n"
                        )

                        for task_output in mismatched_lines:
                            rich_print(f"[red]{task_output}[/red]")

                        rich_print("------------")

                    else:
                        rich_print(
                            f"Problem [green]{Path(task_file.name).stem}[/green] solved !\n"
                            "------------"
                        )

        except Exception:
            sys.stdout = sys.__stdout__
            raise

        finally:
            sys.stdout = sys.__stdout__

            if not self.incorrect_solutions:
                rich_print("[green]WELL DONE![/green]")

                self.clear()
            else:
                rich_print("[red]\nNot all tests passed, please try again[/red]")

    def clear(self) -> None:
        shutil.rmtree(self._temp_directory_path)
        os.remove(self._temp_zip_path)
        logger.info("Working directory is now empty")

    def __call__(self, archive_url: str = None):
        pretty.install()

        self.archive_url = archive_url or pyclip.paste().decode()
        self.download_lesson_archive(self.archive_url)
        self.unpacking(archive_url=self.archive_url)

        def dec(func):
            globals().update({func.__name__: func})
            self.checking_assignments()
            return func

        return dec


fast_test = BeeTester()

if __name__ == "__main__":
    test = BeeTester("../Test_for_Stepik")
    test.checking_assignments()
