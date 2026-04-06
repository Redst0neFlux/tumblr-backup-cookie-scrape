from typing import Tuple, List
import sys
from tumblr_backup.main import main as tumblr_backup
from multiprocessing import set_start_method
from tumblr_backup.login import tumblr_login
from requests import Session
from http.cookiejar import MozillaCookieJar


def read_login_credentials() -> Tuple[str, str]:
    """Reads file called blogs.txt in the same directory as this file.
    The file is structured in the format:

    emailaddress@example.org
    password123
    """
    with open("login.txt", "r") as loginfile:
        username, password = [x.rstrip() for x in loginfile]
    return username, password


def flatten(input_list: List[List[str]]) -> List[str]:
    return [
        item for sublist in input_list for item in sublist
    ]  # The fastest way to flatten a list, without importing additonal code from numpy.


def read_blog_list() -> List[List[str]]:
    """Reads file called blogs.txt in the same directory as this file.
    The file is structured in the format:

    blogname
    --option
    --option2
    blogname2
    --options3 argument
    blogname3
    blogname4

    For a full list of the possible arguments, see https://github.com/cebtenzzre/tumblr-utils/blob/master/docs/usage.md
    Note: the following arguments are always enabled as seen in the backup_blogs functions: --incremental --tag-index --cookiefile www.tumblr.com_cookies.json
    """
    with open("blogs.txt", "r") as blogfile:
        blogs = []
        current_blog = []
        for line in blogfile:
            if not line.startswith("--"): # If the line does not start with --, it is a new blog. The old blog can hence be added to the blogs list and current_blog be cleared.
                blogs.append(flatten(current_blog)) # Turn list of lists into a single list, then append to the list of blogs.
                current_blog = []
            current_blog.append(line.rstrip().split(maxsplit=1)) # Strip newline characters, and then split on the first space.  
    blogs.append(flatten(current_blog)) # Strip newline characters, and then split on the first space.
    blogs.pop(0) # Remove the inital empty list from blogs
    return blogs


def backup_blogs(blogs: List[List[str]]) -> None:
    """Backs up the list of blogs read from blogs.txt
    As tumblr_backup is not designed to be run from a file like this, its arguments have to be passed directly into sys.argv.

    The following default arguments are always enabled:
    --incremental | Only backs up new posts, instead of re-scanning the entire blog (this does mean that edited posts will not be preserved in the archive).
    --tag-index | Creates an archive for each tag, and a file that allows you to browse through them.
    --cookiefile www.tumblr.com_cookies.json | Pulls tumblr login cookies from a file, allowing us to backup dashboard-only blogs.
    """
    for blog in blogs:
        get_login_cookies() # Get login cookies each blog to avoid them expiring
        sys.argv = (
            ["tumblr-backup"]
            + blog
            + ["--incremental", "--tag-index", "--cookiefile", "cookies.txt"] # Default arguments
        )
        tumblr_backup()


def get_login_cookies() -> None:
    username, password = read_login_credentials()
    session = Session()
    session.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 "
        "Safari/537.36"
    )
    session.cookies = MozillaCookieJar("cookies.txt")
    tumblr_login(session, username, password)
    session.cookies.save(ignore_discard=True)


def main() -> None:
    sys.modules["multiprocessing"].set_start_method = (
        lambda _: True # Prevents tumblr_backup from starting its own forkserver, which will cause the progrem to crash if done multiple times.
    )
    set_start_method("forkserver") # Since we have prevented tumblr_backup from starting a forkserver, we now do it ourselves.
    tumblr_backup.__globals__["root_folder"] += ("/blogs") # Makes tumblr_backup put all backed up blogs in the blogs folder

    blogs = read_blog_list()
    backup_blogs(blogs)


if __name__ == "__main__":
    main()
