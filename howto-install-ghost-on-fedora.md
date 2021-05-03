<!--
https://errantruminant.com/ghost-on-fedora/
https://github.com/taw00/howto/blob/master/howto-install-ghost-on-fedora.md
-->

Deploying Ghost on Fedora Linux
===============================

<!--Excerpt-->The combination of Ghost and Fedora Linux gives you a powerful, and relatively simple, platform for blogging. Let me show you how to deploy this popular application stack.

![ghost-fedora-logo.png](appurtenances/ghost-fedora-logo.png)

<span class="pubdate">_Published June 12, 2019 || Updated May 3, 2021_</span>

[Ghost](https://ghost.org/) is a blogging platform. One of the most popular and widely deployed. It's open source (MIT License) and written in JavaScript. It's designed to be beautiful, modern, and relatively simple to use by individual bloggers as well as online publications.

I looked at a whole pile of blogging options when I finally decided to go with Ghost. It checks all the boxes for what I required in a blogging platform: It's well supported, and, by the looks of it, well designed. A platform that embraces [Markdown](https://ghost.org/blog/markdown/) (a critical, must-have feature IMHO) and is easy to use and maintain. All on Linux, of course. And 100% had to be open source. Bonus! Ghost is wildly popular, so it should have some longevity. _But there was a stumbling block for me when first attempting to install the software on my favorite flavor of linux. The installation instructions for Fedora Linux were incomplete and very dated._ I fixed that with this article. Enjoy.

---

**This howto will walk you through:**

* [Installation of the server](#server)
  - Installation of minimal Fedora Linux OS on a VPS system
  - Configure it to be secure (firewalld, SSH keys, fail2ban, etc.)
  - Installation of support packages  
    _. . . nginx, certbot, nodejs, etc._
  - Generation and installation of your SSL cert and keys  
    _. . . via Let's Encrypt and ensure are using TLS/SSL as you should be_
  - Setting that cert to auto renew  
    _. . . via a systemd service, not a hacky crontab or script_
* [Configuration of Nginx](#nginx)
* [Installation and configuration of Ghost](#ghost)  
  _. . . using sqlite3 and not MySQL or MariaDB with is unneeded complexity IMHO_
  - Setting up Ghost to be managed by systemd  
    _. . . and not pm2 or screen or some other less reliable mechanism_
  - Some troubleshooting guidance
* [Email support configuration](#postghostemail)
  - Set up system-level email support
  - Set up email subscriptions via MailChimp
* [Backing everything up](#postghostbackup)
* [Addenda](#addenda) include:
  - [Updates and upgrades](#addendumupgrade)
  - [Redirect a post URL](#addendumredirects)
  - [Multiple blogs](#addendummultiple) on the same server
  - [Structuring your website](#addendumlanding) as landing page + blog

<div class="reference">

**The technical specs (updated as of December 2019):**

* Vultr.com VPS -- 1G RAM, 25G SSD storage, 1vCore CPU
* Fedora Linux 30 (and the latest FirewallD, etc.)
* OS Supplied:
  * Web server: Nginx - nginx-1.16.1-1.fc30.x86_64
  * Database: SQLite - sqlite-3.26.0-6.fc30.x86_64
  * Development: NodeJS - nodejs-10.16.3-1.fc30.x86_64
  * Node.js compiler: node-gyp - node-gyp-3.6.0-7.fc30.noarch
  * Email relayer: sSMTP - ssmtp-2.64-22.fc30.x86_64
  * Let's Encrypt (TLS) commandline frontend: Certbot - certbot-0.39.0-1.fc30.noarch
* Ghost: [downloaded source code zip](https://github.com/TryGhost/Ghost/releases) - 3.1.0

</div>

---

## <span id="server"></span>Install the server

### [0] Install the latest Fedora Linux server

Follow the instructions for "HowTo Deploy and Configure a Minimalistic Fedora Linux Server" found here: <https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md>

### [1] Install additional packages

```sh
# Stuff I like to add to most any installation of linux
sudo dnf install vim-enhanced screen -y
# Development-ish and app-related stuff required by Ghost
# and this installation process
sudo dnf install nginx nodejs node-gyp gcc-c++ make certbot git curl -y
```

### [2] Purchase a domain name and configure DNS at your registrar

Gandi.net is one of my current favorite registrars, but there are many. Purchase a domain, for example, `example.com`. And for the purposes of this article, we'll also assume your blog is `blog.example.com` and your system's IP address is `123.123.123.12`.

Once purchased, edit the DNS tables and point your domain at your new server. The DNS record would look something like: `blog A 1800 123.123.123.12`

If you want the raw domain to route there, then `@ A 1800 123.123.123.12`

### [3] Obtain an SSL (TLS) certificate


Note: `certbot` is the _Let's Encrypt_ client that is used to generate the appropriate
TLS certificate for your domain.

**Generate, fetch, and install your SSL keys**

Note: running certbot requires any webserver that happens to be running on your system to be stopped. If this is a fresh install of the operating system, it is unlikely that anything is running, but here's an example of stopping Nginx:

```sh
sudo systemctl status nginx.service
# If it is running, stop it!
sudo systemctl stop nginx.service
```

In this example, we generate, fetch, and install certs for example.com, www.example.com, and blog.example.com:

```sh
sudo certbot certonly --standalone --domains example.com,www.example.com,blog.example.com --email john.doe@example.com --agree-tos --rsa-key-size 2048
```

Certbot will populate this directory: `/etc/letsencrypt/live/example.com/`

**Setup certbot to auto-renew**

We'll use the built in systemd services to do this:

_Edit `/etc/sysconfig/certbot`_

Set the service PRE_HOOK as such:
```sh
PRE_HOOK="--pre-hook '/usr/bin/systemctl stop nginx.service'"
```

Set the service POST_HOOK as such:
```sh
POST_HOOK="--post-hook '/usr/bin/systemctl start nginx.service'"
```

_Enable and start (--now) the renewal service_
```sh
sudo systemctl enable --now certbot-renew.timer
```

Note: If you edit and change the configuration of `/etc/sysconfig/certbot`, the `certbot-renew.timer` service will have to be restarted for the changes to take effect.

<!--
Old way:
```sh
sudo crontab -e
```

Add this:

```sh
30 2 * * 1 /usr/local/sbin/certbot-auto renew >> /var/log/certbot-auto-renew.log
35 2 * * 1 /usr/bin/systemctl reload nginx.service
```

Save that and exit.
-->

---

## <span id="nginx"></span>Configure Nginx

### [4] Configure SELinux to allow Nginx traffic to flow to Ghost

Nginx relays traffic through port 2368 (in our configuration) which is the port that the Ghost application manages things through. SELinux does not like this.

I was unsuccessful in getting SELinux to work in enforcing mode. Until I, or someone else, figures it out, set SELinux to permissive:

```sh
# This will take immediate effect, but not survive reboot
sudo setenforce permissive
```

To ensure it sticks after reboot:  
Edit `/etc/selinux/config` and set `SELINUX=permissive`

> _Extra credit work:_  
> If you can figure out how to get SELinux to work with ghost proxying things to port 2368, please email me. I got stuck here:
> * I examined `/var/log/audit/audit.log` (after full installation)
> * I even used `audit2why` and `sealert` to analysize things
> * I ran this: `sudo semanage port -a -t http_port_t -p tcp 2368 ; sudo semanage port -l|grep http`
> * I then restarted nginx and tried again. But I couldn't get it to work.

### [5] Crank up nginx

```sh
sudo systemctl start --now nginx.service
```

### [6] Configure `/etc/nginx/conf.d/ghost.conf`

Or better yet, `/etc/nginx/conf.d/example.com.ghost.conf`

```nginx

###
### blog.example.com (SSL/TLS)
###

server {
  server_name blog.example.com;
  #listen 80;
  #listen [::]:80;
  listen 443 ssl http2;
  listen [::]:443 ssl http2;

  # You could set this in ../nginx.conf, but I prefer only editing
  # configuration files under the conf.d/ directory if possible.
  types_hash_max_size 4096;

  # Set this to whatever you want
  # But remember, smaller file sizes are generally better
  client_max_body_size 10M;

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

###
### blog.example.com (non-SSL/TLS)
###

server {
  server_name blog.example.com;
  listen 80;
  listen [::]:80;

  # You could set this in ../nginx.conf, but I prefer only editing
  # configuration files under the conf.d/ directory if possible.
  types_hash_max_size 4096;

  # Set this to whatever you want
  # But remember, smaller file sizes are generally better
  client_max_body_size 10M;

  # Send non-security calls to the secure protocol
  return 301 https://blog.example.com$request_uri;
}

###
### all other .example.com calls
###

server {
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

Note: If you have issues with SSL/TLS (i.e., https calls are not working), troubleshoot away, but if you need to get the site up and https is not an immediate concern, this is how you switch back: Uncomment the `listen` lines associated to port 80 and set `blog.example.com` in the server stanza that services non-ssl to something like `broken.example.com` and then restart the `nginx.service`.

### [7] Check Nginx configuration syntax:

```sh
sudo nginx -t
```

### [8] Reload Nginx configuration:

```sh
sudo systemctl reload nginx.service
```

---

## <span id="ghost"></span>Install Ghost

### [9] Create a ghost user

```sh
# A non-priviledged "normal" user specific for this use.
sudo useradd -c "Ghost Application" ghost
```

### [10] Create Ghost's document root and set permissions

Default webroot for Nginx is `/usr/share/nginx/html`. Note that
`/usr/share` is for static read-only content. Therefore, we want
to create and use our own webroot for Ghost. For this we create
and use `/var/www/ghost`

```sh
# Create docroot/webroot and set permissions
sudo mkdir -p /var/www/ghost
sudo chown -R ghost:ghost /var/www/ghost
sudo chmod 775 /var/www/ghost
```

### [11] Download Ghost

<!--
```sh
# For a specific version, do something like this:
curl -L https://github.com/TryGhost/Ghost/releases/download/2.23.4/Ghost-2.23.4.zip -o ghost.zip
```
-->

```sh
sudo -u ghost curl -L $(curl -sL https://api.github.com/repos/TryGhost/Ghost/releases/latest | jq -r '.assets[].browser_download_url') -o /tmp/ghost.zip
# Note: Downloading to /tmp/ so that any user has permissions to it

# Alternative:
#curl -sL https://api.github.com/repos/TryGhost/Ghost/releases/latest | jq -r '.assets[].browser_download_url' | sudo -u ghost xargs -I GHOST_URL curl -L GHOST_URL -o /tmp/ghost.zip
```

### [12] Unzip/Refresh Ghost application

```sh
sudo -u ghost unzip -uo /tmp/ghost.zip -d /var/www/ghost
sudo rm /tmp/ghost.zip
```

### [13] Install Ghost

```sh
# Navigate to the webroot and install
cd /var/www/ghost
sudo -u ghost npm install --production ; sudo -u ghost npm audit fix
```

### [14] Configure Ghost to use your domain and sqlite3

You'll be editing `config.production.json`.

```sh
# Navigate to the correct directory
cd core/server/config/env/

# Make a backup of the original default configuration
sudo cp -a config.production.json config.production.json--ORIGINAL
```

```sh
# Edit the configation file
sudo -u ghost vim config.production.json
```

Replace the contents with something that looks like this (using your specific information). Then save and exit:

```json
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

> Note, once you have Ghost up and running, create a redundant
> backup of this file. Future updates tend to overwrite it:
> `sudo cp -a config.production.json config.production.json--backup`

### [15] Start Ghost (initial testing)

```sh
# Remember, we are doing this as the ghost user
cd /var/www/ghost ; sudo -u ghost NODE_ENV=production node index.js
#cd /var/www/ghost ; sudo -u ghost npm start --production
```

<!---
```sh
cd /var/www/ghost ; sudo -u ghost NODE_ENV=production node index.js >> /var/www/ghost/content/logs/ghost.log
#cd /var/www/ghost ; sudo -u ghost npm start --production >> /var/www/ghost/content/logs/ghost.log
```
-->


### [16] Test that it works

Browse to `https://blog.example.com` (or whatever your configured domain is).

Once satisfied, shut it down with `^C` in the window that you are using to run ghost from the commandline.

### [17] Configure a Ghost systemd service

Edit the systemd `ghost.service` (as root):

```sh
sudo vim /etc/systemd/system/ghost.service
```

Add this, save, and exit:

```ini
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

### [18] Crank up that Ghost service!

```sh
# You are still your normal working user
sudo systemctl daemon-reload
sudo systemctl start ghost.service
sudo systemctl status ghost.service
sudo systemctl enable ghost.service
```

Test it again.

---

## <span id="postghost"></span>Post install configuration of Ghost

### [19] Set up your admin credentials

Browse to `https://blog.example.com/ghost` and set your credentials promptly.

### [20] Change your theme (if you like)

The default is nice, but there are others. Find a theme you like, download and unzip to `/var/www/ghost/content/themes` and configure in the link provided above.

Some themes to get you started:

* https://colorlib.com/wp/best-free-ghost-themes/
* https://ghost.org/marketplace/
* https://blog.ghost.org/free-ghost-themes/
* https://ghost-o-matic.com/ghost-o-matic/

More themes, but none of which are free:

* https://creativemarket.com/themes/ghost/recent
* https://themeix.com/product-category/ghost-themes/

**Example:**
```sh
sudo su - ghost
cd /var/www/ghost/content/themes
git clone https://github.com/TryGhost/Massively
exit
sudo systemctl restart ghost.service
```
Then browse to <https://blog.example.com/ghost> --> Design --> scroll down to "massively" --> activate

### [21] Troubleshooting

Log in as your normal linux user (not root, not ghost):

```sh
sudo systemctl status ghost.service
sudo journalctl -u ghost.service -f
sudo -u ghost tail -f /var/www/ghost/content/logs/https___blog_example_com.production.log
sudo -u ghost tail -f /var/www/ghost/content/logs/https___blog_example_com.production.error.log

sudo systemctl status nginx.service
sudo journalctl -u nginx.service -f
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## <span id="postghostemail"></span>Configure email support

Your blog needs to be able to email people in two different ways.
1. At the system level: admins, editors, etc. Forgotten passwords. Invites. Etc.
2. A managed mailing list: Subscription feed service (MailChimp) for readers of your website and blog.

First, let's tackle things at the system level . . .

### [22] System-level email: Install sSMTP
```sh
sudo dnf install ssmtp mailx -y
```

mailx is only used to test things more directly. It's not critical for the application. For more discussion on this topic, fee free to visit my related host: <https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md> (Method 2 is the most apropos).

### [23] System-level email: Set up an email account with your domain provider

Something like `noreply@example.com` and set a password. I use Lastpass to generate passwords.

Find out what the name of the smtp hostname is for your domain provider. For example, with gandi.net, it's mail.gandi.net.

They should also list the TLS requirements. Probably TLS and port 587.

### [24] System-level email: Configure sSMTP

**Tell the OS which MTA you are going to be using:**

```sh
sudo alternatives --config mta
```

It will look something like this, select sSMTP with the right number and exit:

```text
There are 3 programs which provide 'mta'.

  Selection    Command
-----------------------------------------------
   1           /usr/bin/esmtp-wrapper
*+ 2           /usr/sbin/sendmail.postfix
   3           /usr/sbin/sendmail.ssmtp

Enter to keep the current selection[+], or type selection number: 3
```

**Configure sSMTP**

For this example, I am using Gandi.net (my domain provider -- each is different), therefore:

* Example SMTP Server: mail.gandi.net:587
* Example username: noreply@example.com
* Example (app) password: kjsadkjbfsfasdfqwfq

_Note, you could use blog.example.com if you wanted to. Up to you and this assumes you have that set up for email. I do not._

Configuring sSMTP is pretty easy, and a bit more obvious than ther MTA, like for example, Postfix.

* Backup the original configuration file:    
  `sudo cp -a /etc/ssmtp/ssmtp.conf /etc/ssmtp/ssmtp.conf-orig`
* Edit ssmtp configuration file:    
  `sudo nano /etc/ssmtp/ssmtp.conf`

Change these settings, or add if they are missing:

```ini
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

**Test that it works "in the raw"**

This is only needed for testing:  
The way this works is that for every user on the system, you need to map    
_username --> email that will work for the --> smtp server_

Edit the ssmtp alias mapping: `sudo nano /etc/ssmtp/revaliases`

Example:

```
root:noreply@example.com:mail.gandi.net:587
ghost:noreply@example.com:mail.gandi.net:587
```

**Monitor it**

```sh
# Either one of these methods should work for you
sudo tail -f /var/log/maillog
#sudo journalctl -f | grep -i ssmtp
```

**Send a test email**

Do this as root or ghost user:

```sh
sudo su - ghost
echo "This is the body of the email. Test. Test. Test." | mail -s "Direct email test 01" -r noreply@example.com someones-email-address@gmail.com
```

### [25] System-level email: Edit config.production.json

```sh
sudo -u ghost vim /var/www/ghost/core/server/config/env/config.production.json
```

Change the `"mail"` stanza to look something like this:

```json
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

> Note (again), once you have Ghost up and running, create a redundant
> backup of this file. Future updates tend to overwrite it:
> `cp -a config.production.json config.production.json--backup`

### [26] System-level email: Restart Ghost and Test

```sh
sudo systemctl restart ghost.service
sudo systemctl status ghost.service
```

Navigate to the admin screens, click Staff, and invite someone (I invited myself for testing purposes). It should send them an email.

Copy that production config to backup now.

```sh
sudo cp -a /var/www/ghost/core/server/config/env/config.production.json /var/www/ghost/core/server/config/env/config.production.json--BACKUP
```

### [27] Mailing list services: Email subscriptions via MailChimp

Automate sending notifications to a mailing list of subscribers for every blog post you write. Integrating Ghost with MailChimp makes this relatively easy. You could use [Ghost's built in email subscriptions](https://docs.ghost.org/faq/enable-subscribers-feature/) + Zapier + Mailchimp, but I like to keep things simple. I just use MailChimp directly:

Direct [Mailchimp integration](https://docs.ghost.org/integrations/mailchimp/)
* Create a [MailChimp](https://mailchimp.com/) account.
* Create two email campaigns: Click into "Campaigns" (on the MailChimp website) and
  1. Create a "Single welcome email" for new subscribers
  2. Create a "Weekly blog updates" that sends an RSS feed summary. See also [these instructions](https://mailchimp.com/features/rss-to-email/).
* Embed an subscribe-by-email widget to the bottom of every entry page by:
  - Click into the "Audience" tab on the MailChimp website.
  - Using the "Manage Audience" dropdown menu, choose "Signup Forms"
  - Click "Embedded Forms"
  - Change the form title to something like "Subscribe to the Example.com Blog!"
  - Click "Condensed"
  - Copy the embedded code that mailchimp provides you.
* Create a "partial" template in `/var/www/ghost/content/themes/casper/partials/` (or for whatever theme you use, I prefer Massively over Casper)  
  Create a file called `custom_mailchimp.hbs` and do this:
```xml
<section class="post-mailchimp">
    Stick the embedded code that MailChimp provides you here.
</section>
```
* Then, edit the `post.hbs` and the `index.hbs` templates.
  - SSH into your blog server.
  - Change directory to `/var/www/ghost/content/themes/casper/` or whatever directory your them lives is.
  - Backup `post.hbs` and `index.hbs` to `post.hbs--original` and `index.hbs--original` respectively.
  - Edit the `post.hbs` file and,  
    Insert `{{> custom_mailchimp }}` right before `{{!-- <section class="post-full-comments">`
  - Edit the `index.hbs` file and,  
    Insert `{{> custom_mailchimp }}` right before `{{!-- <section class="post-full-comments">`
  - If you use customized `index.hbs` and `post.hbs` files, of course edit those instead (customized hbs files is beyond the scope of this document).
* Restart Ghost: `sudo systemctl restart ghost.service`

You should now see an email subscription field at the bottom of each of your blog entries.

### [28] Commenting services: Disqus commenting functionality and other integrations

This isn't really "email" but it is a communication pathway for the consumers of your blog and website. I leave this to the reader to figure out. I don't currently enable commenting on my blog, and thus I haven't really researched this.

* https://docs.ghost.org/integrations/disqus/
* Integrate stuff. For example:
  - https://zapier.com/apps/ghost/integrations
  - https://zapier.com/apps/ghost/integrations/pocket
* Check out the Ghost Forums: https://forum.ghost.org/c/themes

---

## <span id="postghostbackup"></span>Back everything up

You did all this work! You gotta back everything up now. :)

Log in as your normal working user. Not root. Not ghost. Create a back script and copy to a safe place. Edit `vim backup-ghost_blog.example.com.sh` add this and save it.

```sh
#!/usr/bin/bash

URL=blog.example.com
WEBROOT=/var/www/ghost
SERVICENAME=ghost.service

# This script will
# - shut down the ghost and nginx systemd services
# - create an RPM manifest for reference
# - back up ghost and the configurations for nginx, ssmtp, letsencrypt/certbot
#   (this does not back up your OS configuration)
# - restarts the ghost and nginx systemd services

echo "Shutting down ghost and nginx services . . ."
# Shut down ghost and nginx
sudo systemctl stop nginx.service
sudo systemctl stop ${SERVICENAME}
echo ". . . done."

# Back everything up
DATE_YMD=$(date +%Y%m%d)
echo "Grabbing the RPM manifest of this server . . ."
rpm -qa | sort > $HOSTNAME-rpm-manifest-${DATE_YMD}.txt
echo ". . . done."

echo "Creating README file for backup . . ."
echo "\
Critical configuration files (and directories) are:

For Ghost itself:
${WEBROOT}/core/server/config/env/config.production.json
${WEBROOT}/content/themes/
${WEBROOT}/content/data/ghost.db
${WEBROOT}/content/data/redirects.json

For the Ghost systemd service:
/etc/systemd/system/${SERVICENAME}

For mail handling:
/etc/ssmtp/ssmtp.conf
/etc/ssmtp/revaliases

For the webserver:
/etc/nginx/
. . . but especially:
/etc/nginx/nginx.conf
/etc/nginx/conf.d/

For the TLS (SSL) certificates:
/etc/letsencrypt/
/etc/sysconfig/certbot
. . . but especially:
/etc/letsencrypt/live/
/etc/letsencrypt/archive/
/etc/letsencrypt/renewal/
" > ghost-backup-${URL}-${DATE_YMD}-README.md
echo ". . . done."

echo "Backing up Ghost, Nginx, and associated configuration . . ."
sudo tar -czf ./ghost-backup-${URL}-${DATE_YMD}.tar.gz \
  ${WEBROOT} /etc/nginx /etc/ssmtp/revaliases \
  /etc/systemd/system/${SERVICENAME} /etc/ssmtp/ssmtp.conf \
  /etc/letsencrypt /etc/sysconfig/certbot \
  $HOSTNAME-rpm-manifest-${DATE_YMD}.txt \
  ghost-backup-${URL}-${DATE_YMD}-README.md
rm $HOSTNAME-rpm-manifest-${DATE_YMD}.txt ghost-backup-${URL}-${DATE_YMD}-README.md
echo ". . . done."

echo "Starting up ghost and nginx services . . ."
# Start ghost and nginx
sudo systemctl start ${SERVICENAME}
sudo systemctl start nginx.service
echo ". . . done."

echo "Here is your backup tarball, copy it somewhere safe:"
ls -lh ./ghost-backup-${URL}-${DATE_YMD}.tar.gz
```

Save that script, then run it:

```sh
. ./backup-ghost_blog.example.com.sh
```

Then save it somewhere. I `scp` the file to my desktop and then save it to my Keybase filesystem (along with all my backups of everything, by the way). But anywhere inaccessible to the public is fine.

---

## Congratulations! YOU'RE DONE!

Or you  at least done with the initial setup. You now have an end-to-end functioning Ghost blogging platform installed.

Any questions or commentary, you can find me at <https://keybase.io/toddwarner>

---
---

<span id="addenda"></span>

## <span id="addendumupgrade"></span>Addendum: Updates and Upgrades

**Updating the operating system**

Should just work: `sudo dnf upgrade -y --refresh; sudo reboot`

**Upgrading Ghost**

The process is relatively simple.

0. Backup -- See "[Back Everything Up](#backeverythingup)" above

. . . Okay. You are all backed up? Good. You can now continue . . .

1. Download the new tarball (to `/tmp/ghost.zip`)  
   For reference, see "[11] Download Ghost" above. But, for your convenience:
   ```sh
   sudo -u ghost curl -L $(curl -sL https://api.github.com/repos/TryGhost/Ghost/releases/latest | jq -r '.assets[].browser_download_url') -o /tmp/ghost.zip
   ```
2. Navigate to the webroot for your Ghost deployment
   ```sh
   cd /var/www/ghost
   ```
3. Make a convenience backup of your Ghost configuration file:  
   ```sh
   sudo cp -a ./core/server/config/env/config.production.json /tmp/
   ```
4. Shut down the ghost service:
   ```sh
   sudo systemctl stop ghost.service
   ```
5. Deploy new Ghost over top old  
   For reference, see "[Unzip/Refresh Ghost application](#12unziprefreshghostapplication)" and "[Install Ghost](#13installghost)" above. But, for your convenience:
   ```sh
   # Unzip and refresh Ghost into the webroot
   sudo -u ghost unzip -uo /tmp/ghost.zip -d .

   # Install Ghost over top the old installation
   sudo -u ghost npm install --production ; sudo -u ghost npm audit fix
   ```
6. Replace overwritten config file with your convenience backup:
   ```sh
   sudo mv /tmp/config.production.json ./core/server/config/env/
   ```
7. Restart the ghost service:
   ```sh
   sudo systemctl start ghost.service
   ```
8. Browse to your domain and your domain/ghost and check that everything works correctly.
9. Remove the downloaded Ghost zipfile
   ```sh
   sudo rm /tmp/ghost.zip
   ```

---

## <span id="addendumredirects"></span>Addendum: Redirect a Post URL

Situation: Let's say you wrote a blog post about cats and dogs and the URL to get to it is "https://yourdomain/cats-and-dogs" and you shared it out to social media, but what you really want it to be is "https://yourdomain/pets", because soon you are going to update it to contain information about all kinds of pets.

Problem: Changing the _slug_ or _Post URL_ to "pets" instead of "cats-and-dogs" is easy enough in the post editor in the settings widget to the right but then if you shared that post out to anyone, they have the old URL which is now no good.

Solution: Tell Ghost to redirect those old URLs to the new URL
- Edit Ghost's `redirects.json` file:

```sh
# Assumptions:
# - webroot is /var/www/ghost and
# - the editor is vim (nano or any other editor works fine too)
cd /var/www/ghost/content/data
sudo cp -a redirects.json redirects.json--ORIGINAL
sudo -u ghost vim redirects.json
```

- Add the mappings to that file ("fanfiction" redirect is just another example):  
  (_Warning: watch those commas, one too many or too few leads to failure._)


```json
[

{
    "from": "/cats-and-dogs/",
    "to": "/pets/",
    "permanent": true
},

{
    "from": "/fanfiction/",
    "to": "/my-fanfiction-sucks/",
    "permanent": true
}

]
```

- Restart the Ghost service: `sudo systemctl restart ghost.service`
- Test it: browse to the old and new URLs, they should go to the same place.
- You're done!

---

## <span id="addendummultiple"></span>Addendum: Multiple Blogs on One Server

These are not step-by-step instructions but this plus the generalized instructions above should give you enough to figure out how it's done.

- Configure you DNS (via your domain manager, GoDaddy, Gandi, whomever) to point each domain name to the same IP address. For this example, `blog1.example.com` and `blog2.example.com`
- Decide on a port paring. For this example, 2368 for blog1 and 2369 for blog2.
- Instead of `/var/www/ghost` for your webroot, create one for each blog. For example: `/var/www/ghost_blog1` and `/var/www/ghost_blog2` and repeat installation of the Ghost application to each.
- Similarly, `/etc/nginx/conf.d/example.com.ghost.conf` becomes something like `blog1.example.com.ghost.conf` and `blog2.example.com.ghost.conf`
- Similarly, `/etc/systemd/system/ghost.service` becomes `ghost_blog1.service` and `ghost_blog2.service`
- Ensure the hostnames, webroots, and ports for each are reflected everywhere they are referenced:
  - Hostname (URL), Webroot and port: `config.production.json` in each of those `/var/www/ghost_*` trees
  - Webroot only: `ghost_blog1.service` and `ghost_blog2.service`
  - Hostname, Webroot, and port: `blog1.example.com.ghost.conf` and `blog2.example.com.ghost.conf`
- The mail stuff will change a bit. I leave that to you to figure out. :)

I believe that is all. Good luck. For reference, I have three ghost blogs that I host on one machine with no noticeable degradation in performance (small-time blogs, mind you).

---

## <span id="addendumlanding"></span>Addendum: Structure Your Site as a Landing Page + Blog

Ghost natively likes to be a blog with all the articles listed on the front page, but what if you want to lead with a landing page that houses the blog in a separate tab? For example, maybe I am an author and I want the reader to land on a single page that then if they want to read the blog, they navigate to a separate tab and _then_ see the list of articles. You can do that with a bit of routing magic.

As of this writing, [tandemfarms.ag](https://tandemfarms.ag) does just that. If you navigate to the site, it takes you to a short landing page and "Makin' Hay" the blog portion is a tab at the top that then shows you all the blog posts.

**The steps:**

> Assumption for this example: webroot is `/var/www/ghost` and your theme is in `/var/www/ghost/content/themes/Massively_custom/`

0. Make the nginx `.conf` file manage the bare URL instead of the `blog.` URL

   Create an nginx configuration file similar to the one in the above article, but instead of `blog.example.com` being the lead/default domain managed by nginx, change it to what works for you.

   In my case, I switched to the bare domain. I.e., the equivalent of `example.com`. And then I handled `blog.example.com` just like any other `whatever.example.com` calls. Most subdomains you'll want to redirect to `example.com`. If you are converting a website that was a `blog.example.com`-styled website to one that is now `example.com`-styled (like I did), just create a server stanza that redirects all `blog.example.com` calls to `example.com/blog$request_uri`

   This will probably take a bit of experimenting if you are new to this, but it's not that hard.

1. Create the landing page in the admin interface (yourdomain/ghost) just like you create any other post or page.
   _For my example, the _slug_ or _Post URL_ for the page is set to "home". You can set it to whatever: "welcome" or "landing-page", etc._

2. Decide the sub-folder you want your blog to live in.  
   _yourdomain/blog/? yourdomain/journal/? (I chose /blog/ for [tandemfarms.ag/blog](https://tandemfarms.ag/blog/))._

3. Log in (ssh) and create a `custom-landing-page-template.hbs`, something like this:
   ```sh
   cd /var/www/ghost/content/themes/Massively_custom/
   sudo cp -a page.hbs custom-landing-page-template.hbs
   ```

4. Edit that file and change `{{#post}}` to `{{#page}}` and `{{/post}}` to `{{/page}}`  
   _I do not know why the `page.hbs` template uses "post" context, nor do I know why it matters seemingly only in this context._

5. Log into (ssh) your server and edit ghost's `routes.yaml` file:

   ```sh
   cd /var/www/ghost/content/settings
   sudo cp -a routes.yaml routes.yaml--ORIGINAL
   sudo -u ghost vim routes.yaml
   ```

6. Configure `routes.yaml` as such, mapping your Ghost page act as a landing page and your `/blog/` becomes the blog collection of entries.

   ```yaml
   routes:
     /:
       controller: channel
       data: page.home
       template:
         - custom-landing-page-template

   collections:
     /blog/:
       permalink: /blog/{slug}/
       template:
         - index

   taxonomies:
     tag: /tag/{slug}/
     author: /author/{slug}/
   ```

7. Restart the Ghost service: `sudo systemctl restart ghost.service`

8. Test:
   - Browse to yourdomain, you should see your landing page and not your blog.
   - Browse to `yourdomain/blog` and you should see your blog.

9. Give your users a tab at the top to go to your blog
   - Browse to your admin interface: `yourdomain/ghost`
   - In the "Settings" section, click on "Design" and add a tab in the "Navigation" section called "Blog" with a URL of "https://yourdomain/blog" and Save.

> Warning, previously shared links to your posts (not your pages) will be broken. You can fix links with the `redirects.json` file but they have to be the same topology (see [Addendum: Redirect a Post URL](#addendumredirects) above). If the topology wildly changes, you will need to correct things in ways this writer does not yet comprehend.

> You DO NOT need to change their _slug_ or _Post URL_ setting in each post setting.

**You're done! Good luck.**

---
---

<div class="reference">

## Reference

<div style="float: left; width: 43%;">

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

Supporting How-Tos

* taw00. 2019. "How to Deploy and Configure a \[Minimalistic\] Fedora Linux Server." _Github._ <https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md>  
* taw00. 2019. "How to Configure FirewallD and Fail2Ban for Linux." _Github._ <https://github.com/taw00/howto/blob/master/howto-configure-firewalld-and-fail2ban-for-linux.md>
* taw00. 2019. "Configure 'send-only' Email via SMTP Relay." _Github._  <https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md>

</div>
<div style="float: left; width: 10%;">&nbsp;</div>
<div style="float: left; width: 43%;">

Some dated and incomplete "Ghost on Fedora" guides

* <https://www.vultr.com/docs/how-to-deploy-ghost-on-fedora-25>
* <https://blog.ljdelight.com/installing-ghost-blog-on-fedora/>

Ghost configuration guidance and discussion

* General configuration:  
  <https://docs.ghost.org/concepts/config/>
* MariaDB/MySQL instead of SQLite?  
  \[Not recommended\] SQLite is sufficient, and perhaps even more performant, for a blog, no matter the size and popularity, unless the data and database sit on different servers: <https://docs.ghost.org/install/ubuntu/>
* Privacy related things:  
  <https://github.com/TryGhost/Ghost/blob/master/PRIVACY.md>
* Redirects are useful, learn to use them:  
  <https://docs.ghost.org/tutorials/implementing-redirects/>
* Email support using Postfix (not tested):  
  <http://blog.benoitblanchon.fr/postfix-and-ghost/>
* Understanding URLs and Dynamic Routing (`routes.yaml` and more):  
  <https://ghost.org/docs/api/v3/handlebars-themes/routing/>
* Understanding the theme structure and customization:  
  <https://ghost.org/docs/api/v3/handlebars-themes/structure/>  
  <https://ghost.org/tutorials/custom-page-templates/>

This article

* On Github:  
  <https://github.com/taw00/howto/blob/master/howto-install-ghost-on-fedora.md>
* On errantruminant.com (a Ghost-based website):  
  <https://errantruminant.com/ghost-on-fedora/>

</div><div style="clear: both;"></div>
</div>

---

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

Copyright © Todd Warner

