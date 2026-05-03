import sys
from collections.abc import Callable
from http.cookiejar import MozillaCookieJar
from multiprocessing import set_start_method

from requests import Session
from tumblr_backup.login import tumblr_login
from tumblr_backup.main import main as tumblr_backup


def read_login_credentials() -> tuple[str, str]:
    """Reads file called blogs.txt in the same directory as this file.
    The file is structured in the format:

    emailaddress@example.org
    password123
    """
    with open(file="login.txt", mode="r") as loginfile:
        login, password = [x.rstrip() for x in loginfile]
    return login, password


def flatten(input_list: list[list[str]]) -> list[str]:
    # The fastest way to flatten a list, without importing additonal code from numpy.
    return [item for sublist in input_list for item in sublist]


def read_blog_list() -> list[list[str]]:
    """Reads file called blogs.txt in the same directory as this file.
    The file is structured in the format:

    blogname
    --option
    --option2
    blogname2
    --options3 argument
    blogname3
    blogname4
    -N

    For a full list of the possible arguments, see https://github.com/cebtenzzre/tumblr-utils/blob/master/docs/usage.md
    Note: the following arguments are always enabled as seen in the backup_blogs functions: --incremental --tag-index --quiet --cookiefile www.tumblr.com_cookies.json
    """
    with open(file="blogs.txt", mode="r") as blogfile:
        blogs: list[list[str]] = []
        current_blog: list[list[str]] = []
        for line in blogfile:
            if line and not line.startswith("#"):
                if not line.startswith(("-")):
                    # Line is an argument, not a new blog
                    blogs.append(flatten(input_list=current_blog))
                    # Turn list of lists into a single list, then append to the list of blogs.
                    current_blog: list[list[str]] = []
                current_blog.append(line.rstrip().split(maxsplit=1))
                # Strip newline characters, and then split on the first space.
    blogs.append(flatten(input_list=current_blog))
    blogs.pop(0)
    # Remove the inital empty list from blogs
    return blogs


def backup_blogs(blogs: list[list[str]]) -> None:
    """Backs up the list of blogs read from blogs.txt
    As tumblr_backup is not designed to be run from a file like this, its arguments have to be passed directly into sys.argv.

    The following default arguments are always enabled:
    --incremental | Only backs up new posts, instead of re-scanning the entire blog (this does mean that edited posts will not be preserved in the archive).
    --tag-index | Creates an archive for each tag, and a file that allows you to browse through them.
    --cookiefile www.tumblr.com_cookies.json | Pulls tumblr login cookies from a file, allowing us to backup dashboard-only blogs.
    """
    results: dict[str, int] = {"Success": 0, "Failure": 0}
    failed_blogs: list[str] = []
    for blog in blogs:
        get_login_cookies()  # Get login cookies each blog to avoid them expiring
        sys.argv: list[str] = (
            ["tumblr-backup"]
            + blog
            + [
                "--incremental",
                "--tag-index",
                "--quiet",
                "--cookiefile", "cookies.txt",
            ]  # Default arguments
        )
        exit_code: int = tumblr_backup()

        match exit_code:
            case 0 | 5:
                results["Success"] += 1
                print(f"{blog[0]}: Success")
            case 4 | 1:
                results["Failure"] += 1
                failed_blogs.append(blog[0])
                print()
                print(f"{blog[0]}: Failure")
        print("----------------------")
    print(repr(results))
    print("Failed blogs:")
    print("- " + "\n- ".join(failed_blogs))


def get_login_cookies() -> None:
    login: str
    password: str
    login, password = read_login_credentials()
    session = Session()
    session.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 "
        "Safari/537.36"
    )
    session.cookies = MozillaCookieJar(filename="cookies.txt")
    tumblr_login(session, login, password)
    session.cookies.save(ignore_discard=True)


def main() -> None:
    sys.modules["multiprocessing"].set_start_method: Callable = lambda _: True
    # Prevents tumblr_backup from starting its own forkserver, which will cause the progrem to crash if done multiple times.
    set_start_method(method="forkserver")
    # Since we have prevented tumblr_backup from starting a forkserver, we now do it ourselves.
    tumblr_backup.__globals__["root_folder"] += "/blogs"
    # Makes tumblr_backup put all backed up blogs in the blogs folder

    blogs: list[list[str]] = read_blog_list()
    backup_blogs(blogs)


if __name__ == "__main__":
    main()
