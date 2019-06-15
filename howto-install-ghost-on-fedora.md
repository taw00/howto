![ghost-fedora-logo.png](appurtenances/ghost-fedora-logo.png)

# HowTo install the Ghost blogging platform on Fedora

[Ghost](https://ghost.org/) is a blogging platform. One of the most popular and widely deployed. It's open source (MIT License) and written in JavaScript. It's designed to be beautiful, modern, and relatively simple to use by individual bloggers as well as online publications.

I looked at a whole pile of blogging options when I finally decided to go with Ghost. It's well supported, and, by the looks of it, well designed. I was looking for a platform that embraces markdown and is easy to use and maintain. All on Linux, of course. And 100% had to be open source. So here it is.

But there was a stumbling block. The installation instructions for Fedora Linux were incomplete and very dated.

I fixed that. Enjoy.

> _If you are reading this [on another platform](https://github.com/taw00/howto/blob/master/howto-install-ghost-on-fedora.md), the catalyst for this endeavor was <https://blog.errantruminant.com>._

---

This howto will walk you through:

* Installation of minimal Fedora Linux OS on a VPS system
* Configure it to be secure (firewalld, SSH keys, fail2ban, etc.)
* Generation and installation of your Let's Encrypt SSL cert and keys  
  _...so that you are using TLS/SSL as you should be_
* Setting that cert to auto renew  
  _...via a systemd service, not a hacky crontab or script_
* Installation and configuration of Nginx
* Installation and configuration of Ghost  
  _...using sqlite3 and not MySQL or MariaDB with is unneeded complexity IMHO_
* Setting up Ghost to be managed by systemd  
  _...and not pm2 or screen or some other less reliable mechanism_
* Properly setting up email support on the system
* Some troubleshooting guidance
* Backing everything up

The technical specs of what was used to develop my blog and write this howto were...

* Vultr.com VPS -- 1G RAM, 25G SSD storage, 1vCore CPU, and a lot of available bandwidth
* Fedora Linux 30 (and the latest FirewallD, etc.)
* OS Supplied:
  * Web server: Nginx - nginx-1.16.0-3.fc30.x86_64
  * Database: SQLite - sqlite-3.26.0-5.fc30.x86_64
  * Development: NodeJS - nodejs-10.16.0-3.fc30.x86_64
  * Node.js compiler: node-gyp - node-gyp-3.6.0-7.fc30.noarch
  * Email relayer: sSMTP - ssmtp-2.64-22.fc30.x86_64
  * Let's Encrypt (TLS) commandline frontend: Certbot - certbot-0.34.2-3.fc30.noarch
* Ghost - zip file downloaded was 2.23.4

---

## Install the server

### [0] Install the latest Fedora Linux server

Follow the instructions for "HowTo Deploy and Configure a Minimalistic Fedora Linux Server" found here: <https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md>

### [1] Install additional packages

```
# Stuff I like
sudo dnf install vim-enhanced screen -y
# Development-ish and app-related stuff
sudo dnf install nginx nodejs node-gyp make certbot git -y
```

### [2] Purchase a domain name and configure DNS at your registrar

Gandi.net is one of my current favorite registrars, but there are many. Purchase a domain, for example, `example.com`. And for the purposes of this article, we'll also assume your blog is `blog.example.com` and your system's IP address is `123.123.123.12`.

Once purchased, edit the DNS tables and point your domain at your new server. The DNS record would look something like: `blog A 1800 123.123.123.12`

If you want the raw domain to route there, then `@ A 1800 123.123.123.123`

### [3] Obtain an SSL (TLS) certificate


Note: `certbot` is the _Let's Encrypt_ client that is used to generate the appropriate
TLS certificate for your domain.

**Fetch your SSL keys and install them on the system**

```
# In this example, example.com, www.example.com, and
# blog.example.com all will be routable, securely, to this IP
sudo certbot certonly --standalone --domains example.com,www.example.com,blog.example.com --email john.doe@example.com --agree-tos --rsa-key-size 2048
```

Note: If you already have nginx or another webserver running on this host, you may have to pause it before running certbot and then start it up again. I.e., `sudo systemctl stop nginx` ..._then execute the above command, and then_... `sudo systemctl start nginx`

Certbot will populate this directory: `/etc/letsencrypt/live/example.com/`

**Setup certbot to auto-renew**

We'll use the built in systemd services to do this...

_Edit `/etc/sysconfig/certbot`_

Set the service POST_HOOK as such:
```
POST_HOOK="--post-hook '/usr/bin/systemctl reload nginx.service'"
```

_Enable the renewal service_
```
sudo systemctl enable --now certbot-renew.timer
```

<!--
Old way...
```
sudo crontab -e
```

Add this...

```
30 2 * * 1 /usr/local/sbin/certbot-auto renew >> /var/log/certbot-auto-renew.log
35 2 * * 1 /usr/bin/systemctl reload nginx.service
```

Save that and exit.
-->

## Configure Nginx

### [4] Configure SELinux to allow Nginx traffic to flow to Ghost

Nginx relays traffic through port 2368 (in our configuration) which is the port that the Ghost application manages things through. SELinux does not like this.

I was unsuccessful in getting SELinux to work in enforcing mode. Until I, or someone else, figures it out, set SELinux to permissive:

```
# This will take immediate effect, but not survive reboot
sudo setenforce permissive
```

To ensure it sticks after reboot...  
Edit `/etc/selinux/config` and set `SELINUX=permissive`

> _Extra credit work..._  
> If you can figure out how to get SELinux to work with ghost proxying things to port 2368, more power to you. I got stuck here:
> * I examined `/var/log/audit/audit.log` (after full installation)
> * I even used `audit2why` and `sealert` to analysize things
> * I ran this: `sudo semanage port -a -t http_port_t -p tcp 2368 ; sudo semanage port -l|grep http`
> * I then restarted nginx and tried again. But I couldn't get it to work.

### [5] Crank up nginx

```
sudo systemctl start nginx.service && sudo systemctl enable nginx.service
```

### [6] Configure `/etc/nginx/conf.d/ghost.conf`

Or better yet, `/etc/nginx/conf.d/example.com.ghost.conf`

```
server {
  # This manages blog.DOMAIN
  listen 80;
  listen [::]:80;
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  server_name blog.example.com;

  ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

  location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass http://127.0.0.1:2368;
  }
}

server {
  # This redirects www.DOMAIN and the bare DOMAIN to blog.DOMAIN
  listen 80;
  listen [::]:80;
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  server_name example.com www.example.com;

  ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

  return 301 $scheme://blog.example.com$request_uri;
}
```

### [7] Check Nginx syntax:

```
sudo nginx -t
```

### [8] Reload Nginx configuration:

```
sudo systemctl reload nginx.service
```

## Install Ghost

### [9] Create a ghost user

```
sudo useradd -c "Ghost Application" ghost 
```

### [10] Create Ghost's document root and set permissions

Default webroot for Nginx is `/usr/share/nginx/html`. Note that
`/usr/share` is for static read-only content. Therefore, we want
to create and use our own webroot for Ghost. For this we create
and use `/var/www/ghost`

```
# Create docroot/webroot and set permissions
sudo mkdir -p /var/www/ghost
sudo chown -R ghost:ghost /var/www/ghost
sudo chmod 775 /var/www/ghost
```

### [11] Download Ghost

<!--
```
# Direct method for a solitary version
sudo dnf install curl -y
curl -L https://github.com/TryGhost/Ghost/releases/download/2.23.4/Ghost-2.23.4.zip -o ghost.zip
```
-->

```
sudo dnf install curl jq -y
sudo -u ghost curl -L $(curl -sL https://api.github.com/repos/TryGhost/Ghost/releases/latest | jq -r '.assets[].browser_download_url') -o /tmp/ghost.zip
# Note: Downloading to /tmp so that any user has permissions to it

# Alternative:
# curl -sL https://api.github.com/repos/TryGhost/Ghost/releases/latest | jq -r '.assets[].browser_download_url' | sudo -u ghost xargs -I GHOST_URL curl -L GHOST_URL -o /tmp/ghost.zip
```

### [12] Unzip/Refresh Ghost application

```
sudo -u ghost unzip -uo /tmp/ghost.zip -d /var/www/ghost
sudo rm /tmp/ghost.zip
```

### [13] Navigate to `/var/www/ghost` as `ghost` user

```
sudo su - ghost
cd /var/www/ghost
```

### [14] Install Ghost

```
# You are still the ghost user
cd /var/www/ghost ; npm install --production
```

### [15] Configure Ghost to use your domain and sqlite3

```
# You are still the ghost user
cd core/server/config/env/
cp -a config.production.json config.production.json--ORIGINAL
```

Swap out the existing config.production.json with something that looks like this...

```
{
  "url" : "https://blog.example.com",
  "server": {
    "port": 2368,
    "host": "127.0.0.1"
  },
  "database": {
    "client": "sqlite3",
    "connection": {
      "filename": "/var/www/ghost/content/data/ghost.db"
    }
  },
  "mail": {
    "transport": "Direct"
  },
  "logging": {
    "level": "info",
    "rotation": {
      "enabled": true
    },
    "transports": ["file", "stdout"]
  },
  "paths": {
    "contentPath": "/var/www/ghost/content"
  },
  "privacy": {
    "useUpdateCheck": true,
    "useGravatar": false,
    "useRpcPing": true,
    "useStructuredData": true
  }
}
```

### [16] Start Ghost (initial testing)

```
# You are still the ghost user
cd /var/www/ghost ; NODE_ENV=production node index.js
#cd /var/www/ghost ; npm start --production
```

<!--
```
cd /var/www/ghost ; NODE_ENV=production node index.js >> /var/www/ghost/content/logs/ghost.log
#cd /var/www/ghost ; npm start --production >> /var/www/ghost/content/logs/ghost.log
```
-->


### [17] Test that it works

Browse to `https://blog.example.com` (or whatever your configured domain is).

Once satisfied, shut it down with `^C` in the window that you are using to run ghost from the commandline.

### [18] Configure a Ghost systemd service

Log in as your normal linux user (not root, not ghost).

Edit the systemd `ghost.service`...

```
sudo vim /etc/systemd/system/ghost.service
```

Add this, save, and exit...

```
[Unit]
Description=ghost
After=network.target

[Service]
Type=simple
WorkingDirectory=/var/www/ghost
User=ghost
Group=ghost
Environment=NODE_ENV=production
ExecStart=/usr/bin/node index.js
Restart=on-failure
SyslogIdentifier=ghost

[Install]
WantedBy=multi-user.target
```

### [20] Crank up that Ghost service!

```
# You are still your normal working user
sudo systemctl daemon-reload
sudo systemctl start ghost.service
sudo systemctl status ghost.service
sudo systemctl enable ghost.service
```

Test it again.

## Post install configuration

### [21] Set up your admin credentials

Browse to `https://blog.example.com/ghost` and set your credentials promptly.

### [22] Change your theme (if you like)

The default is nice, but there are others. Find a theme you like, download and unzip to `/var/www/ghost/content/themes` and configure in the link provided above.

Some themes to get you started:

* https://colorlib.com/wp/best-free-ghost-themes/
* https://ghost.org/marketplace/
* https://blog.ghost.org/free-ghost-themes/

**Example:**
```
sudo su - ghost
cd /var/www/ghost/content/themes
git clone https://github.com/TryGhost/Massively
exit
sudo systemctl restart ghost.service
```
Then browse to <https://blog.example.com/ghost> --> Design --> scroll down to "massively" --> activate

### [23] Troubleshooting

Log in as your normal linux user (not root, not ghost)...

```
sudo systemctl status ghost.service
sudo journalctl -u ghost.service -f
sudo -u ghost tail -f /var/www/ghost/content/logs/https___blog_example_com.production.log
sudo -u ghost tail -f /var/www/ghost/content/logs/https___blog_example_com.production.error.log

sudo systemctl status nginx.service
sudo journalctl -u nginx.service -f
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Configured email support

Your blog needs to be able to email people. Forgot your password? Invites to admins? Etc.

### [24] Install sSMTP
```
sudo dnf install ssmtp mailx -y
```

mailx is only used to test things more directly. It's not critical for the application. For more discussion on this topic, fee free to visit my related host: <https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md> (Method 2 is the most apropos).

### [25] Set up an email account with your domain provider

Something like `noreply@example.com` and set a password. I use Lastpass to generate passwords.

Find our what the name of the smtp hostname is for your domain provider. For example, with gandi.net, it's mail.gandi.net.

They should also list the TLS requirements. Probably TLS and port 587.

### [26] Configure sSMTP

**Tell the OS which MTA you are going to be using...**

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

**Configure sSMTP**

For this example, I am using Gandi.net (my domain provider -- each is different), therefore...

* Example SMTP Server: mail.gandi.net:587
* Example username: noreply@example.com
* Example (app) password: kjsadkjbfsfasdfqwfq

_Note, you could use blog.example.com if you wanted to. Up to you and this assumes you have that set up for email. I do not._

Configuring sSMTP is pretty easy, and a bit more obvious than ther MTA, like for example, Postfix.

* Backup the original configuration file:    
  `sudo cp -a /etc/ssmtp/ssmtp.conf /etc/ssmtp/ssmtp.conf-orig`
* Edit ssmtp configuration file:    
  `sudo nano /etc/ssmtp/ssmtp.conf`

Change these settings, or add if they are missing...

```
Debug=YES                                    # For now, stick that at the very top of the config file
MailHub=mail.gandi.net:587                   # SMTP server hostname and port
RewriteDomain=example.com                    # The host the mail appears to be coming from
FromLineOverride=YES                         # Allow forcing the From: line at the commandline
UseSTARTTLS=YES                              # Secure connection (SSL/TLS) - don't use UseTLS
TLS_CA_File=/etc/pki/tls/certs/ca-bundle.crt # The TLS cert
AuthUser=noreply@example.com                 # The mail account at my domain provider
AuthPass=kjsadkjbfsfasdfqwfq                 # The password for the mail account

# Keeping in these notes for reference
#root=noreply@example.com                    # Who gets all mail to userid < 1000
#MailHub=smtp.mail.yahoo.com:587             # SMTP server hostname and port
#MailHub=smtp.gmail.com:587                  # SMTP server hostname and port
#Hostname=localhost                          # The name of this host
```

**Test that it works "in the raw"...**

This is only needed for testing...  
The way this works is that for every user on the system, you need to map    
_username --> email that will work for the --> smtp server_

Edit the ssmtp alias mapping: `sudo nano /etc/ssmtp/revaliases`

Example:

```
root:noreply@example.com:mail.gandi.net:587
ghost:noreply@example.com:mail.gandi.net:587
```

**Monitor it...**

```
# Either one of these methods should work for you
sudo tail -f /var/log/maillog
#sudo journalctl -f | grep -i ssmtp
```

**Send a test email...**

Do this as root or ghost user...

```
sudo su - ghost
echo "This is the body of the email. Test. Test. Test." | mail -s "Direct email test 01" -r noreply@example.com someones-email-address@gmail.com
```

### [27] Edit config.production.json

```
sudo -u ghost vim /var/www/ghost/core/server/config/env/config.production.json
```

Change the `"mail"` stanza to look something like this:

```
  "mail": {
    "from": "'Example Blog' <noreply@example.com>",
    "transport": "sendmail",
    "options": {
        "port": 587,
        "host": "mail.gandi.net",
        "secureConnection": false,
        "auth": {
          "user": "noreply@example.com",
          "password": "kjsadkjbfsfasdfqwfq"
        }
    }
  },
```

### [28] Restart Ghost and Test

```
sudo systemctl restart ghost.service
sudo systemctl status ghost.service
```

Navigate to the admin screens, click Staff, and invite someone (I invite myself of course). It should send them an email.

Copy that production config to backup now.

```
sudo cp -a /var/www/ghost/core/server/config/env/config.production.json /var/www/ghost/core/server/config/env/config.production.json--BACKUP
```

### [29] Email subscriptions and Disqus commenting functionality

***This section is not complete yet***

* https://docs.ghost.org/integrations/disqus/
* Email subscriptions:  
  Currently
  [experimenting](https://docs.ghost.org/faq/enable-subscribers-feature/). You
  can also integrate [Mailchimp](https://docs.ghost.org/integrations/mailchimp/).
  Not all themes support it. YMMV.
* Integrate stuff. For example...
  - https://zapier.com/apps/ghost/integrations
  - https://zapier.com/apps/ghost/integrations/pocket
* Check out the Ghost Forums: https://forum.ghost.org/c/themes

## Back everything up

You did all this work! You gotta back everything up now. :)

Log in as your normal working user. Not root. Not ghost. Create a back script and copy to a safe place...

Edit `vim backup-ghost.sh` add this and save it...


```
#!/usr/bin/bash

# This script will
# - shut down the ghost and nginx systemd services
# - create an RPM manifest for reference
# - back up ghost and the configurations for nginx, ssmtp, letsencrypt/certbot
#   (this does not back up your OS configuration)
# - restarts the ghost and nginx systemd services

echo """"
# Shut down ghost and nginx
sudo systemctl stop ghost.service
sudo systemctl stop nginx.service

# Back everything up
DATE_YMD=$(date +%Y%m%d)
rpm -qa | sort > $HOSTNAME-rpm-manifest-${DATE_YMD}.txt
sudo tar -cvzf ./$HOSTNAME-ghost-on-fedora-${DATE_YMD}.tar.gz \
  /var/www/ghost /etc/nginx /etc/ssmtp/revaliases \
  /etc/systemd/system/ghost.service /etc/ssmtp/ssmtp.conf \
  /etc/letsencrypt /etc/sysconfig/certbot \
  $HOSTNAME-rpm-manifest-${DATE_YMD}.txt
rm $HOSTNAME-rpm-manifest-${DATE_YMD}.txt

# Start ghost and nginx
sudo systemctl start ghost.service
sudo systemctl start nginx.service

echo "Here is your backup tarball, copy it somewhere safe:"
ls -lh ./$HOSTNAME-ghost-on-fedora-${DATE_YMD}.tar.gz
```

Save that script, then run it...

```
. ./backup-ghost.sh
```

## Congratulations! YOU'RE DONE!

...at least done with the initial setup. You now have an end-to-end functioning Ghost blogging platform installed.

Any questions or commentary, you can find me at <https://keybase.io/toddwarner>

---

## Reference

#### Getting help

* Ghost: <https://ghost.org/>
* Ghost Forum: <https://forum.ghost.org/>
* Ghost Docs: <https://docs.ghost.org/>
* Fedora Project: <https://start.fedoraproject.org/> (docs, ask Fedora, etc)
* Fedora's Community Blog: <https://communityblog.fedoraproject.org/>
* Fedora on IRC: <https://fedoraproject.org/wiki/IRC>
* Ask Fedora: <https://ask.fedoraproject.org/c/community>
* Some Fedora Community thing: <https://discussion.fedoraproject.org/>

#### Other resources and inspirations

* Installing the OS: <https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md>
* FirewallD: <https://github.com/taw00/howto/blob/master/howto-configure-firewalld-and-fail2ban-for-linux.md>
* Email SMTP setup: <https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md>

&nbsp;

* Dated ghost on fedora guide (old and incomplete): <https://www.vultr.com/docs/how-to-deploy-ghost-on-fedora-25>
* Another dated ghost on fedora guide (old and incomplete):<https://blog.ljdelight.com/installing-ghost-blog-on-fedora/>
* Initial configuration guidance and discussion: <https://docs.ghost.org/concepts/config/>
* MariaDB/MySQL instead of SQLite? &mdash;Not recommended&mdash; SQLite is sufficient (and perhaps even more performant) for a blog, no matter the size and popularity, unless the data and database sit on different servers: <https://docs.ghost.org/install/ubuntu/>
* Privacy related things: <https://github.com/TryGhost/Ghost/blob/master/PRIVACY.md>

&nbsp;

* This article on Github: <https://github.com/taw00/howto/blob/master/howto-install-ghost-on-fedora.md>
* This article on blog.errantruminant.com: <https://blog.errantruminant.com/howto-install-the-ghost-blogging-platform-on-fedora/>

---

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
