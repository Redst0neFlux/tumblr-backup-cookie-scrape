# tumblr-backup-wrapper
Back up a list of tumblr blogs (for use in automated backups).

Quick python package setup using pip: <br/>
`python3 -m venv venv` <br/>
`source ./venv/bin/activate` <br/>
`python3 -m pip install .` <br/>
Create an "app" at https://www.tumblr.com/oauth/apps. Follow the instructions there; most values entered don't matter.
Run `tumblr-backup --set-api-key API_KEY`, where API_KEY is the OAuth Consumer Token from the app created in the previous step.

And to run:<br/>
`source ./venv/bin/activate`<br/>
`python3 main.py`<br/>
`deactivate`<br/>

Put blogs to backup in blogs.txt<br/>
Put username and password in login.txt (needed to backup dashboard-only blogs)

Used projects:
- https://github.com/cebtenzzre/tumblr-utils
