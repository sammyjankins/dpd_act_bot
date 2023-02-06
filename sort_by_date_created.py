import os
import pathlib
import datetime
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib

import secrets


def sort_to_dirs(dir_to_sort: str) -> None:
    """Sorts photos by creation date into folders."""

    folder_name = ''
    for f_name in os.listdir(dir_to_sort):
        file = pathlib.Path(f'{dir_to_sort}/{f_name}')
        ctime = datetime.datetime.fromtimestamp(file.stat().st_ctime).strftime("%d.%m.%Y")

        if folder_name != ctime:
            folder_name = ctime
            os.mkdir(f'{dir_to_sort}/{folder_name}')
        target_dir = os.path.join(os.curdir, dir_to_sort, folder_name)
        shutil.move(os.path.join(os.curdir, dir_to_sort, f_name), target_dir)


def archive(dir_to_arch: str, arch_name: str) -> None:
    """Archive and delete photos."""
    shutil.make_archive(arch_name, 'zip', dir_to_arch)
    shutil.rmtree(dir_to_arch)


def send(filename: str, to: str, subject: str) -> None:
    """Send by email and remove file."""

    smtp_obj = smtplib.SMTP(secrets.SMTP_SERVER, port=secrets.SMTP_PORT)
    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = secrets.SMTP_FROM
    msg['To'] = to

    body_part = MIMEText(subject, 'plain')
    msg.attach(body_part)

    with open(filename, 'rb') as file:
        msg.attach(MIMEApplication(file.read(), Name=filename))

    smtp_obj.starttls()
    smtp_obj.login(secrets.SMTP_FROM, secrets.SMTP_PASS)

    smtp_obj.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp_obj.quit()

    os.remove(filename)


if __name__ == '__main__':
    sort_to_dirs('photo')
    archive('photo', 'photo')
    send('photo.zip', secrets.EMAIL_TO, secrets.EMAIL_SUBJECT)
