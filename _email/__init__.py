import smtplib
from datetime import datetime, timedelta, timezone
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from config import email_content_template, email_from_addr, email_password, log


def _format(s: str):
  _name, _addr = parseaddr(s)
  return formataddr((Header(_name, 'utf-8').encode(), _addr))


def send(to: str, e_str: str):
  msg = MIMEMultipart()

  msg['From'] = _format('Tencent Server <%s>' % email_from_addr)
  msg['To'] = _format('Exception Receive <%s>' % to)
  msg['Subject'] = Header('Spider Exception', 'utf-8').encode()

  e_str = e_str.replace('<', '(')
  e_str = e_str.replace('>', ')')
  e_str = e_str.replace('\n', '<br>')
  e_str = e_str.replace(' ', '&nbsp;')
  content = email_content_template.replace('__exception__', e_str)
  content = content.replace('__datetime__',
                            datetime.now(timezone(timedelta(hours = 8))).strftime('%Y-%m-%d %H:%M:%S'))
  msg.attach(MIMEText(content, 'html', 'utf-8'))

  server = smtplib.SMTP_SSL('smtp.163.com', 994)

  try:
    server.set_debuglevel(1)
    server.login(user = email_from_addr, password = email_password)
    server.send_message(msg)
  except BaseException as e:
    log.exception(e)
    log.error('[eMail] Send failed')
  finally:
    server.quit()
