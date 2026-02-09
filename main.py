from re import split as resplit
from time import sleep
from typing import Tuple, List
from selenium.webdriver import Firefox, FirefoxOptions, FirefoxService
from selenium.webdriver.common.by import By
from netscape_cookies import to_netscape_string
import sys
from tumblr_backup.main import main as tumblr_backup
from multiprocessing import set_start_method

def read_login_credentials() -> Tuple[str, str]:
    """Reads file called blogs.txt in the same directory as this file.
    The file is structured in the format:

    emailaddress@example.org
    password123
    """
    with open("login.txt", "r") as loginfile:
        username, password = loginfile.readlines()
    return username, password

def create_firefox_driver() -> Firefox:
    """Creates a headless browser to provide automated control of a web page (in our case tumblr)."""
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.binary_location = "/usr/bin/firefox"
    service = FirefoxService(executable_path="/usr/bin/geckodriver")
    return Firefox(options=options, service=service)

def login_to_tumblr(driver: Firefox, username: str, password: str) -> List[dict]:
    driver.get("https://tumblr.com/login")
    email_input = driver.find_element(By.CSS_SELECTOR, "[aria-label=email]")
    password_input = driver.find_element(By.CSS_SELECTOR, "[aria-label=password]")
    login_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Log in']")
    email_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()
    sleep(10) # Wait for cookies to load.
    return driver.get_cookies()

def save_cookies_to_file(cookie_data: List[dict]) -> None:
    """Converts exported tumblr login cookies from selenium to Netscape format, for tumblr_backup to use with the cookiejar library.
    The netscape_cookies library does not add the "# Netscape HTTP Cookie File" header, so we do it ourselves."""
    with open("www.tumblr.com_cookies.json", "w") as cookiefile:
        cookiefile.write("# Netscape HTTP Cookie File")
        cookiefile.write(to_netscape_string(cookie_data))

def flatten(input_list: List[List[str]]) -> List[str]:
    return [item for sublist in input_list for item in sublist] # The fastest way to flatten a list, without importing additonal code from numpy.

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
    Note: the following arguments are always enabled as seen in the backup_blogs functions: --incremental --tag-index --cookiefile www.tumblr.com_cookies.json"""
    with open("blogs.txt", "r") as blogfile:
        blogs = []
        current_blog = []
        for line in blogfile:
            if not line.startswith("--"): # If the line does not start with --, it is a new blog. The old blog can hence be added to the blogs list and current_blog be cleared.
                blogs.append(flatten(current_blog)) # Turn list of lists into a single list, then append to the list of blogs.
                current_blog = []
            current_blog.append(line.rstrip().split(maxsplit=1)) # Strip newline characters, and then split on the first space.
    blogs.append(flatten(current_blog)) # Turn list of lists into a single list, then append to the list of blogs.
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
        sys.argv = ["tumblr-backup"] + blog + ["--incremental", "--tag-index", "--cookiefile", "www.tumblr.com_cookies.json"]
        tumblr_backup()

def main() -> None:
    tumblr_backup.__globals__["multiprocessing"].set_start_method = lambda _: True # Prevents tumblr_backup from starting its own forkserver, which will cause the progrem to crash if done multiple times.
    set_start_method('forkserver') # Since we have prevented tumblr_backup from starting a forkserver, we now do it ourselves.

    username, password = read_login_credentials()
    driver = create_firefox_driver()
    cookie_data = login_to_tumblr(driver, username, password)
    driver.quit()
    save_cookies_to_file(cookie_data)
    blogs = read_blog_list()
    backup_blogs(blogs)

if __name__ == "__main__":
    main()