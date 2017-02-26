# HowTo: Configure "send-only" Email via a 3rd Party SMTP Relay for Linux

I want to be able to send automated alerts and whatnot so that my phone buzzes
when something bad happens on a remote system that I manage. There are a number
of ways you can do this, but I found the easiest is to simply pump automated
email through a 3rd party email vendor to myself, or a group of people.

You do that by configuring a ["Mail Transfer
Agent"](https://en.wikipedia.org/wiki/Message_transfer_agent). I'm going to
illustrate how to do this with two different MTAs:

1. **Postfix** - An all-singing and all-dancing MTA that is the successor to
   Sendmail on almost all Linux/Unix systems
2. **sSMTP** - An MTA that only performs this use case: Send via 3rd party SMTP
   server

> Note, these instructions have been tested on the Red Hat family of linuxes
> &mdash;Fedora, CentOS, and Red Hat Enterprise Linux&mdash; but they should be
> easily adaptable to any unix/linux. Check out the references at the end for
> further discussion on this topic.

----

## Prep: Burner Email and Google Group

For this tutorial, create two mail-able indentities.

* A burner email account. Example, nfdasd@yandex.com (or nfdasd@yahoo.com, etc.)
* A google group to send notifications. Example, my-notifications@googlegroups.com

_Note, these are all made-up examples, of course._

Let's talk about each of these...

#### Burner email account.<br />_...example, `nfdasd@yandex.com`_

Using a single purpose email account is important. If for whatever reason that
account is compromised, your personal email is put at risk. For example, if my
personal google account were compromised, I would be in a world of hurt. We
don't want that. Sure sing app-passwords reduces that possibility, and sure we
compromise ourselves all the time by linking applications to our account,
but... don't add one more when you don't have.

I am using yandex.com as an example, but you can use gmail.com, yahoo.com,
whomever. I use something like Lastpass'es password generator to cycle through
random usernames until I find one I like (alphanumeric and 6 or 8 characters).
Or just pound randomly on the keyboard. That works too. :)

* Create an email account

[Yahoo](https://mail.yahoo.com), [Google](https://mail.google.com),
[Yandex](https://mail.yandex.com)

Caveat: Yandex and Yahoo like many providers, now require an associated cell
phone number. They let you create an account temporarily without one, but
eventually they force you to cough up your cell phone number. I don't know if
we can avoid this anymore unless we set up our own domain for this purpose.
That may be a separate HowTo.

* Set up an app password

In order to use a scripted interface with most 3rd party accounts, they will
provide you some means to access the account with a password that is not your
login password. The password allows certain activities on the account but not
"admin" activities.

With Yandex, you do this in `Gear icon > Settings > Security > App password`.
Create a label, copy the generated password. Save that for later.

With Yahoo, you do this in `Gear icon > Account info > Account Security`. Here
you _must_ turn on 2-factor authentication and you will then have access to the
"Generate app password" button. Choose "Other app" and create the password.
Save that for later.

* Get your email provider's SMTP server information

Search for your email provider's smtp domain and port and any special
requirements to use it.

For yandex.com...

  - `smtp.yandex.com` is the server
  - 587 is the port. 465 is supported, but don't use it (dated).
  - Username: username@yandex.com
  - Password: App password. And it _must_ be set to use this service.

For yahoo.com...

  - `smtp.mail.yahoo.com` is the server
  - 587 is the port. 465 is supported, but don't use it (dated).
  - Username: username@yahoo.com
  - Password: App password. And it _must_ be set to use this service.

For google.com (not tested for this exercise)...

  - `smtp.gmail.com` is the server
  - 587 is the port. 465 is supported, but don't use it (dated).
  - Username: username@gmail.com
  - Password: your password. I'm unsure if a separate app password is required.
  - Browse to <https://mail.google.com>, click on Settings, Forwarding/IMAP.
    Enable IMAP to alert gmail to place sent mail in the sent folder.


#### Create a Google Group to serve as your "message bus"

Instead of sending alert emails directly to some individual personal account,
send alerts to a Google Group. It will serve like a message bus of events and
historical record. Additionally, any number of interested parties can subscribe
to the group in order to receive alerts. Finally, a group allows you control
over the message you get: All email, daily digest, web-only.

* Browse to <https://groups.google.com>
* Create a group. Our example is, `my-notifications`
* Set permissions so that it is invite only
* Set a description
* Add two members to it directly: The burner email address you just created and
  your personal email address
* Set the burner address to not receive email (web-view only)
* Send a test email to <my-notifications@googlegroups.com> from one of those
  group members.
* You should receive that email.

----

## Choose your MTA poison: Postfix or sSMTP

----

### METHOD 1 - Postfix: Configure your Fedora Linux server to send email with Postfix

Postfix is the swiss-army-knife of
[MTA](https://en.wikipedia.org/wiki/Message_transfer_agent)s. And, to be
honest, it is not really any more complicated than setting up sSMTP. But it is
a bigger tool that is overkill for this use case, so... You decide. Here are
Postfix configuration instructions...

Summary of next steps...

* Install the postfix and mailx packages
* Tell the OS which MTA you are going to be using
* Configure Postfix
* Start and enable the Postfix systemd service
* Send test email

#### Install the postfix and mailx packages

Easy peasy...

For Fedora Linux...

```
sudo dnf install -y postfix mailx
```

For CentOS or Red Hat Enterprise Linux...

```
sudo yum install -y postfix mailx
```

#### Tell the OS which MTA you are going to be using...

```
sudo alternatives --config mta
```

It will look something like this, select Postfix with the right number and exit...

```
There are 3 programs which provide 'mta'.

  Selection    Command
-----------------------------------------------
   1           /usr/bin/esmtp-wrapper
*  2           /usr/sbin/sendmail.postfix
 + 3           /usr/sbin/sendmail.ssmtp

Enter to keep the current selection[+], or type selection number: 2
```

#### Configure Postfix

For this example, I am using Yandex, therefore...

* Server: smtp.yandex.com:587
* Example username: nfdasd@yandex.com
* Example (app) password: kjsadkjbfsfasdfqwfq


Configuring postfix is pretty easy, though not entirely obvious.

* Backup the original configuration file:    
  `sudo cp -a /etc/postfix/main.cf /etc/postfix/main.cf-orig`
* Edit postfix configuration file:    
  `sudo nano /etc/postfix/main.cf`

Change these settings, or add if they are missing...

```
relayhost = [smtp.yandex.com]:587
#relayhost = [smtp.mail.yahoo.com]:587
#relayhost = [smtp.gmail.com]:587
smtp_use_tls = yes
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options =
smtp_tls_CAfile = /etc/ssl/certs/ca-bundle.crt
# These two additional settings only used if using port 465
#smtp_tls_wrappermode = yes
#smtp_tls_security_level = encrypt
```

Other options to examine suggested by other howtos...

```
# Note: user+alias@domain subaddressing is not supported by all email providers, yandex included
recipient_delimiter = +
mailbox_size_limit = 0
```

* Edit SMTP username and password in postfix sasl file:    
  `sudo nano /etc/postfix/sasl_passwd`    

```
[smtp.yandex.com]:587 nfdasd@yandex.com:kjsadkjbfsfasdfqwfq
#[smtp.mail.yahoo.com]:587 nfdasd@yahoo.com:kjsadkjbfsfasdfqwfq
#[smtp.gmail.com]:587 nfdasd@gmail.com:kjsadkjbfsfasdfqwfq
```

That file has your password in it. Lock it down:
`sudo chmod 600 /etc/postfix/sasl_passwd`

* "Compile" that password file:    
  `sudo postmap /etc/postfix/sasl_passwd`

It should produce a file called `/etc/postfix/sasl_passwd.db`

_Note: If you see permission errors, check ownership and permissions in that
directory: `ls -l /etc/postfix`_


#### Start and enable the Postfix systemd service

If you haven't enabled it upon reboot, do it now...

```
sudo systemctl enable postfix.service
```

Start it up...

```
sudo systemctl start postfix.service    # if not previously started
#sudo systemctl restart postfix.service # if already started
#sudo systemctl stop postfix.service    # if you need to stop it
#sudo systemctl status postfix.service  # is it already started?
```

Monitor it...

```
sudo journalctl -u postfix.service -f -n25
```

#### Send a test email...

For this example, I am using Yandex and Google Groups, therefore...

* Server: smtp.yandex.com:587
* Example username: nfdasd@yandex.com
* Example (app) password: kjsadkjbfsfasdfqwfq
* Example personal email: your-email-address@example.com
* Example group email: my-notifications@googlegroups.com

Send an email to someone directly...

```
echo "This is the body of the email. Test. Test. Test." | mail -s "Direct email test 01" -r nfdasd@yandex.com your-email-address@example.com
```

If that works fine, send an email to your google group...

```
echo "This is the body of the email. Test. Test. Test." | mail -s "Group email test 01" -r nfdasd@yandex.com my-notifications@googlegroups.com
```

If you are monitoring the system, log with that journalctl command, you should see something like...

```
Feb 15 17:50:59 mn0 postfix/pickup[20874]: D5100DC63A: uid=1000 from=<nfdasd@yandex.com>
Feb 15 17:50:59 mn0 postfix/cleanup[21887]: D5100DC63A: message-id=<58a49503.tOGKlZXDLpKqWJQt%nfdasd@yandex.com>
Feb 15 17:50:59 mn0 postfix/qmgr[19914]: D5100DC63A: from=<nfdasd@yandex.com>, size=469, nrcpt=1 (queue active)
Feb 15 17:51:04 mn0 postfix/smtp[21889]: D5100DC63A: to=<my-notifications@googlegroups.com>, relay=smtp.yandex.com[77.88.21.38]:587, delay=4.3, delays=0.03/0.04/2.5/1.7, dsn=2.0.0, status=sent (250 2.0.0 Ok: queued on smtp3j.mail.yandex.net as 1487181064-lyDmMVZ9eP-p2c0s157)
Feb 15 17:51:04 mn0 postfix/qmgr[19914]: D5100DC63A: removed
```


----


### METHOD 2 - sSMTP: Configure your Fedora Linux server to send email with sSMTP

sSMTP is a much simpler service than Postfix. Its singular purpose is to send
email through an smtp relay. It is much lighter weight than Postfix, but
setting things up for this use case are not worlds easier than Postfix. There
are advantages to using a lighter weight program to do the things you need to
do. Six of one; half dozen of the other. I am currently using this method
personally. You decide. :)

Summary of next steps...

* Install the ssmtp and mailx packages
* Tell the OS which MTA you are going to be using
* Configure sSMTP    
  _note, sSMTP is not required to be running as a daemon - no service to manage._
* Send test email


#### Install the ssmtp and mailx packages

Easy peasy...

For Fedora Linux...

```
sudo dnf install -y ssmtp mailx
```

For CentOS or Red Hat Enterprise Linux...

```
sudo yum install -y ssmtp mailx
```


#### Tell the OS which MTA you are going to be using...

```
sudo alternatives --config mta
```

It will look something like this, select sSMTP with the right number and exit...

```
There are 3 programs which provide 'mta'.

  Selection    Command
-----------------------------------------------
   1           /usr/bin/esmtp-wrapper
*+ 2           /usr/sbin/sendmail.postfix
   3           /usr/sbin/sendmail.ssmtp

Enter to keep the current selection[+], or type selection number: 3
```

#### Configure sSMTP

Just like with the Postfix instructions, for this example, I am using Yandex,
therefore...

* Server: smtp.yandex.com:587
* Example username: nfdasd@yandex.com
* Example (app) password: kjsadkjbfsfasdfqwfq

Configuring sSMTP is pretty easy, and only a bit more obvious than Postfix.

* Backup the original configuration file:    
  `sudo cp -a /etc/ssmtp/ssmtp.conf /etc/ssmtp/ssmtp.conf`
* Edit ssmtp configuration file:    
  `sudo nano /etc/ssmtp/ssmtp.conf`

Change these settings, or add if they are missing...

```
Debug=YES                                    # For now, stick that at the very top of the config file
#root=nfdasd@yandex.com                      # Who gets all mail to userid < 1000
MailHub=smtp.yandex.com:587                  # SMTP server hostname and port
#MailHub=smtp.mail.yahoo.com:587             # SMTP server hostname and port
#MailHub=smtp.gmail.com:587                  # SMTP server hostname and port
RewriteDomain=yandex.com                     # The host the mail appears to be coming from
#Hostname=localhost                          # The name of this host
FromLineOverride=YES                         # Allow forcing the From: line at the commandline
UseSTARTTLS=YES                              # Secure connection (SSL/TLS) - don't use UseTLS
TLS_CA_File=/etc/pki/tls/certs/ca-bundle.crt # The TLS cert
AuthUser=nfdasd@yandex.com                   # The mail account
AuthPass=kjsadkjbfsfasdfqwfq                 # The password for the mail account
```

* Edit ssmtp alias mapping: `sudo nano /etc/ssmtp/revaliases`

The way this works is that for every user on the system, you need to map    
_username --> email that will work for the --> smtp server_

Example:

```
root:nfdasd@yandex.com:smtp.yandex.com:587
bob:nfdasd@yandex.com:smtp.yandex.com:587
#root:nfdasd@yahoo.com.com:smtp.mail.yahoo.com:587
#root:nfdasd@gmail.com.com:smtp.gmail.com:587
```

Monitor it...

```
sudo tail -f /var/log/maillog
```

#### Send a test email...

Just like with the Postfix instructions, for this example, I am using Yandex
and Google Groups, therefore...

* Server: smtp.yandex.com:587
* Example username: nfdasd@yandex.com
* Example (app) password: kjsadkjbfsfasdfqwfq
* Example personal email: your-email-address@example.com
* Example group email: my-notifications@googlegroups.com

Send an email to someone directly...

```
echo "This is the body of the email. Test. Test. Test." | mail -s "Direct email test 01" -r nfdasd@yandex.com your-email-address@example.com
```

If that works fine, send an email to your google group...

```
echo "This is the body of the email. Test. Test. Test." | mail -s "Group email test 01" -r nfdasd@yandex.com my-notifications@googlegroups.com
```

----

## All done!

Now you have a scripting pattern for using with something like a monitoring system or cronjobed scripts, etc.

Good luck. Send comments or feedback: <t0dd@protonmail.com>

----

## References

* [Configure Postfix to use Gmail as a Mail Relay](https://www.howtoforge.com/tutorial/configure-postfix-to-use-gmail-as-a-mail-relay/)
* [Fedora Linux Postfix Documentation](https://docs.fedoraproject.org/en-US/Fedora/25/html/System_Administrators_Guide/s1-email-mta.html) - Educational, if not overly helpful
* [Yandex email send rate limits](https://yandex.com/support/mail/spam/sending-limits.xml) -- 35 per day
* [Google email send rate limits](https://support.google.com/mail/answer/22839?hl=en) -- 500 per day
* [Webpage talking about various send-limits](http://www.yetesoft.com/free-email-marketing-resources/email-sending-limit/) -- not sure how accurate

----

> **A big caveat about 3rd party email providers!**
> 
> I used yandex.com for this example (I have since included yahoo and gmail
> information as well). I recently discovered that Yandex has among the most
> limiting send rates (how many emails you are allowed to send per X
> time-period) of all the large email providers. If you send over 35 emails per
> day via Yandex, they begin rejecting them as spam (then you wait 24 hours for
> a reset).
>
> Google is a better choice at 500 per day, and Yahoo seems to allow 100 per
> hour (I believe). But those services still have their limitations if
> something goes wrong with your application. Plus, email is slow. :)
>
> **Recommendation**
>
> It is getting harder and harder to use these large 3rd party email providers
> for this kind of activity. For general use they likely work just fine, but if
> you absolutely MUST have rock solid and fast alerting, you should probably
> look at SMS messaging (maybe a later howto?), a dedicated email server that
> you manage yourself, or use some other alerting service. For the rest of us,
> the Google, Yahoo, and maybe even Yandex solution works well enough.

