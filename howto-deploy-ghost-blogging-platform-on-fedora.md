# HowTo: Deploy Ghost blogging platform on Fedora

### [0] Purchase a Domain

Gandi.net is one of my current favorite registrars, but there are many. Purchase a domain, for example, `example.com`. And we'll assume your blog will be `blog.example.com`

## Install the server

### [1] Install the latest Fedora Linux server

HowTo Deploy and Configure a Minimalistic Fedora Linux Server: <https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md>

### [2] Install additional packages

```
# Stuff I like
sudo dnf install vim-enhanced screen -y
# Development-ish and App-related stuff
sudo dnf install nginx nodejs node-gyp make certbot -y
```

Note:  `certbot` is the _Let's Encrypt_ client, so you can set up SSL to work with your domain.

### [3] Obtain an SSL (TLS) certificate

**Point your domain at your new server**

Visit your domain registrar and point your domain at your system's IP address. The DNS record would look something like: `blog A 1800 123.123.123.12`

If you want the raw domain to route there, then `@ A 1800 123.123.123.123`

**Fetch your SSL keys and install them on the system**
```
# In this example, TLS will function correctly if you route these
# three domains to this IP address.
sudo certbot certonly --standalone --domains example.com,www.example.com,blog.example.com --email john.doe@example.com --agree-tos --rsa-key-size 2048
```

Note: If you already have nginx or another webserver running on this host, you will have to pause it before running certbot and then start it up again. I.e., `sudo systemctl stop nginx` ...then execute the above command, and then... `sudo systemctl start nginx`

This will populate this directory: `/etc/letsencrypt/live/example.com/`

**Setup certbot to auto-renew**

We'll use the built in systemd services to do this...

_Edit `/etc/sysconfig/certbot`_

Set the service POST_HOOK as such:
```
POST_HOOK="--post-hook '/usr/bin/systemctl reload nginx.service'"
```

_Enable the service_
```
sudo systemctl enable --now certbot-renew.timer
```

<!--
Old way...
```
sudo crontab -e
```

And add this...

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

And to ensure it sticks after reboot...  
And then edit `/etc/selinux/config` and set `SELINUX=permissive`

> _Extra credit work._  
> If you can figure out how to get SELinux to work with ghost proxying things to port 2368, more power to you. I got stuck here:
> * I examined `/var/log/audit/audit.log` (after full installation)
> * I even used `audit2why` and `sealert` to analysize things
> * I ran this: `sudo semanage port -a -t http_port_t -p tcp 2368 ; sudo semanage port -l|grep http`
> * I then restarted nginx and tried again. Dunno. Not working

### [5] Crank up nginx

```
sudo systemctl start nginx.service && sudo systemctl enable nginx.service
```

### [6] Configure `/etc/nginx/conf.d/ghost.conf`

Or better yet, `/etc/nginx/conf.d/example.com.ghost.conf`

```
server {

  listen 80;
  listen [::]:80;
  listen 443 ssl http2;
  listen [::]:443 ssl http2;

  server_name example.com www.example.com;

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

10. Create Ghost's Nginx's document root and set permissions

Default webroot is `/usr/share/nginx/html`. Note that `/usr/share` is for static read-only content. Therefore, we want to create and use our own webroot for Ghost. For this we create and use `/var/www/ghost`

```
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

Browse to `https://blog.example.com` (well, your configured domain).

Now shut it down. `^C` in that window that you are using to run ghost.

### [18] Configure a ghost service

Log out of the ghost user and do this as your normal working user sudoing these actions.

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

### [22] Change your theme

The default is nice, but there are others. You find a theme like, download and unzip to `/var/www/ghost/content/themes` and configure in the link provided above.

Some themes to get you started:
* https://colorlib.com/wp/best-free-ghost-themes/
* https://ghost.org/marketplace/
* https://blog.ghost.org/free-ghost-themes/

### [23] Mail and Disqus (commenting) functionality

* https://docs.ghost.org/integrations/disqus/
* Email signup (TODO)
* Integrate stuff. For example...
  - https://zapier.com/apps/ghost/integrations
  - https://zapier.com/apps/ghost/integrations/pocket
* Check out the Ghost Forums: https://forum.ghost.org/c/themes

### [24] Troubleshooting

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

## Email

Your blog needs to be able to email people. Forgot your password? Invites to admins? Email subscribers? You get it.

### [25] Install sSMTP
```
sudo dnf install ssmtp mailx -y
```

You are not going to use mailx in this example, but you may if you want to do direct testing with the command `mail`. See <https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md> (Method 2) for more information.

### [26] Set up an email account with your domain provider

Something like `noreply@example.com` and set a password. I use Lastpass to generate passwords.

Find our what the name of the smtp server is for your domain provider. For example, with gandi.net, it's mail.gandi.net.

They should also list the TLS requirements. Probably TLS and port 587.

### [27] Configure sSMTP

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
#root=noreply@example.com                    # Who gets all mail to userid < 1000
MailHub=mail.gandi.net:587                   # SMTP server hostname and port
#MailHub=smtp.mail.yahoo.com:587             # SMTP server hostname and port
#MailHub=smtp.gmail.com:587                  # SMTP server hostname and port
RewriteDomain=example.com                    # The host the mail appears to be coming from
#Hostname=localhost                          # The name of this host
FromLineOverride=YES                         # Allow forcing the From: line at the commandline
UseSTARTTLS=YES                              # Secure connection (SSL/TLS) - don't use UseTLS
TLS_CA_File=/etc/pki/tls/certs/ca-bundle.crt # The TLS cert
AuthUser=noreply@example.com                 # The mail account at my domain provider
AuthPass=kjsadkjbfsfasdfqwfq                 # The password for the mail account
```

**Test that it works "in the raw"...**

This is only needed for testing. Edit ssmtp alias mapping: `sudo nano /etc/ssmtp/revaliases`

The way this works is that for every user on the system, you need to map    
_username --> email that will work for the --> smtp server_

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


### [28] Edit `config.production.json`

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

### [29] Restart Ghost and Test

```
sudo systemctl restart ghost.service
sudo systemctl status ghost.service
```

Navigate to the admin screens, click Staff, and invite someone (I invite myself of course). It should send them an email.


## Congratulations! YOU'RE DONE!

...at least with the initial setup. You now have an end-to-end functioning Ghost blogging platform installed.

Any questions or commentary, you can find me at <https://keybase.io/toddwarner>

---

## References

* <https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md>
* <https://www.vultr.com/docs/how-to-deploy-ghost-on-fedora-25>
* <https://blog.ljdelight.com/installing-ghost-blog-on-fedora/>
* Initial configuration: <https://docs.ghost.org/concepts/config/>
* Not recommended. MariaDB/MySQL is unneeded for a blog, no matter the size and popularity, unless the data and database sit on different servers (which is also unneeded): <https://docs.ghost.org/install/ubuntu/>
* Privacy related things: <https://github.com/TryGhost/Ghost/blob/master/PRIVACY.md>
* Email: <https://github.com/taw00/howto/blob/master/howto-configure-send-only-email-via-smtp-relay.md>
* Article on Github: <https://github.com/taw00/howto/blob/master/howto-deploy-ghost-blogging-platform-on-fedora.md>
* Article on blog.errantruminant.com: <https://blog.errantruminant.com/howto-deploy-the-ghost-blogging-platform-on-fedora/>

