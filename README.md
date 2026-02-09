# tumblr-backup-cookie-scrape
Back up a list of tumblr blogs, using selenium to scrape login cookies.

System requirements:
- firefox
- geckodriver

Quick python package setup: <br/>
`python3 -m venv venv` <br/>
`source ./venv/bin/activate` <br/>
`python3 -m pip install -r requirements.txt` <br/>

And to run:<br/>
`source ./venv/bin/activate`<br/>
`python3 main.py`<br/>
`deactivate`<br/>

Put blogs to backup in blogs.txt<br/>
Put username and password in login.txt (needed to backup dashboard-only blogs)

Used projects:
- https://github.com/cebtenzzre/tumblr-utils
- https://github.com/seleniumhq/selenium
- https://github.com/r44cx/netscape-cookies
