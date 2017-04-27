# A Happy Hour Reminder Bot

![butter-pass](https://coubsecure-s.akamaihd.net/get/b56/p/coub/simple/cw_timeline_pic/13c249557a5/32028402520b27a9e0bff/med_1433953458_image.jpg)

_dio_: What is my purpose?

_msyriac_: You send emails.

_dio_: Oh my god...

This bot sends out a reminder email, and a second email with a randomly chosen location for a Happy Hour meet-up.

# Suggesting new places

Add a comma-delimited row to `listOfPlaces.csv` containing the name of the
place and a weight expressing your desire to go the place on a scale from 0
(would never go) to 1 (would always be up for going there).

# Usage

Edit `settings.yaml`, `email_first_reminder.txt`, `email_location.txt` and `listOfPlaces.csv`.

Then,


```
./dionysus.py start settings.yaml
```

to start a background process.

```
./dionysus.py stop
```

to stop any background processes.

```
./dionysus.py restart settings.yaml
```

to restart with new settings.
