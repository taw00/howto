# HowTo Install Wordpress on Fedora Linux, MariaDB, and Nginx

> **Disclaimer:** This is a work in progress and fine-tuning of your wordpress deployment will be required. Please do your own due diligence and spend some time studying hardening your website, best practices for file and directory permissions, etc. etc.

This document describes the minimum process for getting up and running with Wordpress on your own Fedora Linux system leveraging Nginx as your webserver and MariaDB (mysql) as the database.

Though this document will get you up and running, there are a few things still left incomplete that I will add later.
  1. Backing things up -- remedial instructions at end of document
  2. Fully vetted directory and file permissions
  3. No instructions for ftp setup yet
  4. Making any necessary SELinux configuration changes

Assumptions:
  * The reader has moderate linux administrative skills
  * The reader understands how to register a domain and remedially manipulate DNS records

Values used in this document:  
_Note that values you should replace with your own are marked with a superscripted <sup>*</sup> character._
* IP: `198.51.100.35`<sup>*</sup>
* Domain: `example.com`<sup>*</sup>
* Subdomain: `blog.example.com`<sup>*</sup>
* Subdomain used for testing: `blogtest.example.com`<sup>*</sup>
* Wordpress root: `/usr/share/wordpress`
* Wordpress config: `/etc/wordpress/wp-config.php`
* Nginx access.log: `/var/log/nginx/example/access.log`<sup>*</sup>
* Nginx error.log: `/var/log/nginx/example/error.log`<sup>*</sup>
* Nginx website config: `/etc/nginx/conf.d/example.conf`<sup>*</sup>
* php-fpm unix socket path: `unix:/var/run/php-fpm/www.sock`
* php-fpm unix port config: `127.0.0.1:9000` --but not used
* php-fpm error_log: `/var/log/php-fpm/error.log`
* mariadb system user: `mysqladmin` --the default already-created user
* DB root password: `'this is the admin password'`<sup>*</sup>
* Site database - DB_NAME: `examplewpdb`<sup>*</sup>
* Site db user - DB_USER: `'sqluser'`<sup>*</sup>
* Site db user - DB_HOST: `'localhost'`
* Site db password - DB_PASSWORD: `'my example website for the win'`<sup>*</sup>

## [0] Deploy and configure minimal Linux server

Reference: ["HowTo: Deploy and Configure a Fedora Linux Operating System"](https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md)

And, for now, turn off selinux...  
```
sudo setenforce 0
```

## [1] Register a domain and point it at this server's IP address

**Register and configure your domain and subdomain...**  
_Note that this is performed at your domain provider._
1. Register a domain at your domain provider: [Gandi](https://gandi.net), [Bluehost](https://www.bluehost.com), or [Godaddy](https://godaddy.com), ...wherever. There are [a lot](https://www.icann.org/registrar-reports/accredited-list.html) of them.
2. Add a DNS record for your subdomain redirecting it towards the IP address of your wordpress server. The DNS record would look something like: `blogtest   A   1800   198.51.100.35`

It will take a couple minutes to percolate out, but then the mapping should be in place for, `blogtest.example.com` (use a test domain until ready to publish to the world).

**Verify that the mapping has percolated across the internet...**  
_Note that this is performed from your laptop or any linux machine on the internet._
```
dig blogtest.example.com
host blogtest.example.com
```

## [2] Install the software

**Install...**
```
sudo dnf install -y nginx php-fpm
sudo dnf install -y wordpress
sudo dnf install -y php-mysqlnd mariadb-server
```

**Disable the apache webserver (just to be sure)...**

```
# Ensure apache is stopped and disabled
sudo systemctl disable httpd.service
sudo systemctl stop httpd.service
```

**Enable Nginx webserver, php-fpm, and the Mariadb (Mysql) database...**
```
sudo systemctl enable nginx.service php-fpm.service mariadb.service
```

## [3] Punch a whole in your firewall and set up reasonable connection rate limits...

This makes ports 80 (http) and 443 (https) accessible by the outside world.

```
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-rich-rule='rule service name=http accept limit value=10/s'
sudo firewall-cmd --permanent --add-rich-rule='rule service name=https accept limit value=10/s'
sudo firewall-cmd --reload
```

## [4] Set up the Database

**Start the database...**
```
sudo systemctl start mariadb.service
```

**Set your root password for the database...**

```
sudo mysqladmin -u root password
```

**Create a database instance for site...**

```
sudo mysqladmin create examplewpdb -u root -p
```

**Create privileged user/password for the `examplewpdb` database**

The web app uses these credentials to run. Use the standard `mysql` client program for this step. The `-D mysql` option attaches to the built-in `mysql` database where privileges are stored.

...commands and output shown mixed. **[bold]** is our input...  

`$`**`sudo mysql -D mysql -u root -p`**

`Enter password:`**`<enter the admin password>`**

```
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 6
Server version: 10.1.18-MariaDB MariaDB Server

Copyright (c) 2000, 2016, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
```
`MariaDB [mysql]>`**`GRANT ALL PRIVILEGES ON examplewpdb.* TO 'sqluser'@'localhost' IDENTIFIED BY '<insert your db password here>';`**
```
Query OK, 0 rows affected (0.00 sec)
```
`MariaDB [mysql]>`**`FLUSH PRIVILEGES;`**
```
Query OK, 0 rows affected (0.01 sec)
```
`MariaDB [mysql]>`**`QUIT;`**
```
Bye
```

## [5] Webserver (Nginx) and Wordpress prepwork

**On the filesystem...**
```
# Nginx stuff
mkdir -p /var/log/nginx/example
touch /var/log/nginx/example/{access,error}.log

# Wordpress stuff
sudo cp /etc/wordpress/wp-config.php /etc/wordpress/wp-config-original.php
sudo cp /usr/share/wordpress/wp-config-sample.php /etc/wordpress/wp-config.php
```

## [6] Configure webserver (Nginx)

**Create `/etc/nginx/conf.d/example.conf`...**
_Note, I am sure there are ways to reduce the redundancy in this configuration. Suggestions welcome._

```
server {
    listen 80;
    listen [::]:80;

    server_name blogtest.example.com;

    access_log /var/log/nginx/example/access.log;
    error_log  /var/log/nginx/example/error.log;
    types_hash_max_size 4096;

    location / {
        root /usr/share/wordpress;
        index index.php index.html index.htm;

        if ( -f $request_filename ) {
            expires 30d;
            break;
        }

        if ( !-e $request_filename ) {
            rewrite ^(.+)$ /index.php?q=$1 last;
        }
    }

    location ~ .php$ {
        #fastcgi_pass 127.0.0.1:9000;
        fastcgi_pass  unix:/var/run/php-fpm/www.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME /usr/share/wordpress/$fastcgi_script_name;
        fastcgi_param PATH_INFO       $fastcgi_script_name;
        include /etc/nginx/fastcgi_params;
    }


server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name blogtest.example.com;

    access_log /var/log/nginx/example/access.log;
    error_log  /var/log/nginx/example/error.log;
    types_hash_max_size 4096;

    ########### For now, we error on https ###########
    return 302 https://$server_name$request_uri;

    #
    # TLS stuff
    # Note, later you can troubleshoot with, for example:
    #   openssl s_client -debug -connect blog.example.com:443
    #
    # Uncomment only after certs are created
    #ssl_certificate /etc/nginx/ssl/example.com/blog.example.com.cert.pem;
    #ssl_certificate_key /etc/nginx/ssl/example.com/blog.example.com.key.pem;

    # generated with: openssl dhparam -out /etc/ssl/dhparam.pem 4096
    # Uncomment only after certs are created
    #ssl_dhparam /etc/ssl/dhparam.pem;

    ssl_protocols TLSv1.2 TLSv1.1;
    ssl_prefer_server_ciphers on;
    ssl_ciphers AES256+EECDH:AES256+EDH:!aNULL;
    ssl_session_cache shared:TLS:2m;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1;

    # Set HSTS to 365 days
    add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains';

    location / {
        root /usr/share/wordpress;
        index index.php index.html index.htm;
 
        if ( -f $request_filename ) {
            expires 30d;
            break;
        }
 
        if ( !-e $request_filename ) {
            rewrite ^(.+)$ /index.php?q=$1 last;
        }
    }
 
    location ~ .php$ {
        #fastcgi_pass 127.0.0.1:9000;
        fastcgi_pass  unix:/var/run/php-fpm/www.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME /usr/share/wordpress/$fastcgi_script_name;
        fastcgi_param PATH_INFO       $fastcgi_script_name;
        include /etc/nginx/fastcgi_params;
    }
}
```

**Test it...**
```
sudo nginx -t
```

## [7] Adjust PHP configurations

`php.ini` restricts things a bit much. Make these changes. We are choosing arbitrarily large numbers here. Adjust as needed over time.

**Boost your file size limits (I like to a note in the comments that I changed the default)...**
```
;upload_max_filesize = 2M
; adjusted -todd
upload_max_filesize = 128M
```
```
;post_max_size = 8M
; adjusted -todd
post_max_size = 256M
```
```
;max_execution_time = 30
; adjusted -todd
max_execution_time = 300
```

## [8] Configure Wordpress

**Edit `/etc/wordpress/wp-config.php`**

Set these relevant configurations...
```
define( 'DISALLOW_FILE_MODS', false ); // allows for "Add New" updates
define( 'WP_HOME', 'http://blogtest.example.com' );
define( 'WP_SITEURL', 'http://blogtest.example.com' );
define( 'DB_NAME', 'examplewpdb' );
define( 'DB_USER', 'sqluser' );
define( 'DB_PASSWORD', '<insert my db password here' );
define( 'DB_HOST', 'localhost' );
```

&nbsp;
**Visit this site and replace the appropriate values in `wp-config.php`:** <https://api.wordpress.org/secret-key/1.1/salt/>

These values are unique per visit to the link above. They can be regenerated and replaced at any time. You do not have to securely tuck them away in case of disaster or anything...

```
define('AUTH_KEY',         'xNr[ble+oeC$w=IK[#&eTU3 2]rK p_HXLQ@r/`Voq|(y|n~6@|y>ZR3HO&VW~,^');
define('SECURE_AUTH_KEY',  'Sb|d.V?lIAFnQC W T^]~PXg9ED8}/7}=`4+c0?|R*@L5(PNGpL+hn/1PhPM{0,F');
define('LOGGED_IN_KEY',    '~CAN6x1; |b%-Np=PW8{-UfzEr)6-|Pp{`gU4e};I4UaTyeS4~`#uPf5`DU3DQ!A');
define('NONCE_KEY',        'umJZx{E{]%*VRLoc!.M&k[_]0AF;bSG7|+yeso.-TdRZXhFHH>F:YA ]nukkw9aI');
define('AUTH_SALT',        ')bjowz-qLY^+.9ui9mh{W,>LDZMtiRAp ;~VjfiZu4K9!YJMdZ<]w08KxrGUW&I)');
define('SECURE_AUTH_SALT', ']i~h^xhn!G/+G&<jdq1`:->B|z7y;3}?5bycV,Myx=,(|mHO=K+|h{<H16S|XPc$');
define('LOGGED_IN_SALT',   '_=VEE&h{=RQ-!q ,1X8j-a&)C%tfqLi^,B0MW |Y0:1#[B{y4gj-at*mFg|rvm-v');
define('NONCE_SALT',       'sY*OQrBg117%=1bcp&2Z+@*rMp.y@-tq]g=:w=1+o$B|J[AS?-VLOe3IYpG),~[q');
```

### Directory and File Permissions

_A word of caution, my views here are, at best, imperfect. I will keep updating this howto over time._

Wordpress on Fedora installs assuming Apache will be the webserver serving most content and therefore most everything beneath `.../wp-content` is permissioned `apache:ftp`. Our instructions here leverage `php-fpm` (fastcgi) behind the scenes serving up content to Nginx that then serves it to the user. `php-fpm` is configured to also act with permissions `apache:apache`.

Permission problems most often arise when you are writing content to the website versus pulling information from it. Hence, it is advised that you set permissions on the directory trees as mentioned above ("TL;DR section").

**General rules of thumb...**
* `php-fpm` (fastcgi) operates with `apache:apache` permissions
* `root:root` permissions for static content is fine, generally
* Don't arbitrarily change all the permissions under your document root `/usr/share/worpress/` It's bad practice and potentially very insecure.
* `/usr/share/wordpress/wp-content` can remain `root:root` but do this...  
  ```
  sudo chmod u+s /usr/share/wordpress/wp-content/{uploads,plugins,themes,upgrade}
  ```

More stuff (but dated): <https://nealpoole.com/blog/2011/04/setting-up-php-fastcgi-and-nginx-dont-trust-the-tutorials-check-your-configuration/>


### (Re)start services and monitor logs

```
#sudo systemctl restart nginx.service php-fpm.service
sudo systemctl start nginx.service php-fpm.service
```

**Monitor these logs...**  
_(open a terminal for each of these commands)_

```
sudo tail -f /var/log/nginx/example/error.log
sudo tail -f /var/log/nginx/example/access.log
sudo tail -f /var/log/php-fpm/error.log
sudo tail -f /var/log/php-fpm/www-error.log
# Way too noisy, but can be valuable...
sudo journalctl -xe
sudo journalctl -u nginx
```

## [9] Try it out!

**Visit your website:** <http://blogtest.example.com>

You should see a freshly minted Wordpress welcome page.

If not, pick through the information found in those log files and see if you can figure out what error you made. Most of my errors are related to typos. :)

## [10] INSTALLED! Now build that website!

Congratulations. You now have Wordpress running. Now the real work begins...

**Build your website...**  
_For the rest of the process, here are some good starting points._
* <https://wordpress.org/support/article/how-to-install-wordpress/#finishing-installation>
* <https://wordpress.org/support/article/first-steps-with-wordpress/>

## [10] Take it to "production"

Is your build-out complete? Time to make it a "production" website. Once you feel you are at a good place with your test site, you need remove "test" from your domain and you need to enable TLS (i.e., what we used to call SSL).

### Switch from "test site" to "production site"...

* Visit your domain registrar and add a DNS record redirecting to your IP addresss for `blog` or `www` &mdash;or whatever you want the subdomain to be&mdash; instead of `blogtest` or `wwwtest`
* Change the appropriate test values you set in the configuration files in `/etc/nginx/conf.d/` and `/etc/wordpress/`
* Restart Nginx: `sudo systemctl restart nginx.service`
* Test your new configuration: `http://blog.example.com`
* Lock down the database access a bit more -- <https://mariadb.com/kb/en/library/mysql_secure_installation/>
   ```
   # As root, run this command and answer the prompted questions
   # as such (given our currently documented setup)...
   # Answer these questions as such ...
   # Change the root password? [Y/n] n
   # Remove anonymous users? [Y/n] y
   # Disallow root login remotely? [Y/n] y
   # Remove test database and access to it? [Y/n] y
   # Reload privilege tables now? [Y/n] y
   mysql_secure_installation
   ```

### Enable TLS...

Log into root fully. Install `socat` and `acme.sh`.

```
# Login to root
sudo su -
```

```
# Install socat (mini-webserver) and the acme tools. Re-source root's '~/.bashrc' file
dnf install socat -y
curl https://get.acme.sh | sh
. ~/.bashrc
```

> Note that the acme installer will perform 3 actions:
> 
> 1. Create and copy `acme.sh` to your home dir ($HOME): `~/.acme.sh/`  
>    All certs will be placed in this folder too.
> 2. Create alias for: `acme.sh=~/.acme.sh/acme.sh`
> 3. Create daily cron job to check and renew the certs if needed.

Set these temp environment variables to make things easier...
```
DOMAIN=example.com
SITE=blog.${DOMAIN}
```

Issue your TLS certificate (using our blog.example.com example)
```
# This will populate ~/.acme.sh/$SITE/ with certs and keys and such
# If your DNS is not set up, this will fail.
systemctl stop nginx
acme.sh --issue --standalone -d $SITE
systemctl start nginx
```

**Install your cert and key to an appropriate directory to be used by Nginx...**
```
# We're still root...
mkdir -p /etc/nginx/ssl/$DOMAIN

acme.sh --install-cert -d $SITE \
--fullchain-file /etc/nginx/ssl/$DOMAIN/$SITE.cert.pem \
--key-file       /etc/nginx/ssl/$DOMAIN/$SITE.key.pem  \
--reloadcmd     "systemctl force-reload nginx"
```

**Populate openssl dhparams to `/etc/ssl/`...**
```
# We're still root...
openssl dhparam -out /etc/ssl/dhparam.pem 4096
```

**Edit your configuration file in `/etc/nginx/conf.d/` adding in certificate information...**
  * Comment out the line starting with `return 302`..."
  * Uncomment the lines that pertain to the above generated `*.pem` files.
  * Doublecheck that the paths are correct and the files exist in the `/etc/nginx/ssl` tree.

**Edit `/etc/wordpress/wp-config.php`...**

Replace `WP_HOME` and `WP_SITEURL` settings with `https` instead of `http`.

**Restart Nginx and test your new website...**
  * Restart Nginx: `sudo systemctl restart nginx.service`  
    ***If a failure occurs, you probably typo'ed something (check those paths!) or didn't use the acme.sh `--install-cert command` as described.***
  * Test your new, now more secure, configuration: `https://blog.example.com`

&nbsp;

---

## All done!

Comments? Suggestions? Please let me know how this can be improved: <https://keybase.io/toddwarner>

&nbsp;<br />&nbsp;

---

## Addendum

### Addendum - references
* Excellent article by the esteemable Paul Frields: <https://fedoramagazine.org/howto-install-wordpress-fedora/>
* <https://www.if-not-true-then-false.com/2011/install-nginx-php-fpm-on-fedora-centos-red-hat-rhel/>
* <https://www.itzgeek.com/web/wordpress/install-wordpress-with-nginx-on-fedora-21.html>
* Hosting Wordpress: <https://codex.wordpress.org/Hosting_WordPress>
* Hardening Wordpress: <https://codex.wordpress.org/Hardening_WordPress>
...backing things up
* Wordpress Backups: <https://codex.wordpress.org/WordPress_Backups>
* Backing up the database: <https://stackoverflow.com/a/13484728>  
  ...and restoration: <http://webcheatsheet.com/SQL/mysql_backup_restore.php>  
  ...other thoughts: <http://www.nilinfobin.com/mysql/how-to-login-in-mariadb-with-os-user-without-password/>
* Controlling bash history: <https://stackoverflow.com/a/29188490> and <https://www.guyrutenberg.com/2011/05/10/temporary-disabling-bash-history/>

### Addendum - backing things up...

Probably not complete, but a good starting point is to back up...
  * `/etc/nginx`
  * `/etc/wordpress`
  * `/etc/php-fpm`
  * `/etc/php.ini`
  * `/usr/share/wordpress/wp-content`
  * `/usr/share/wordpress/wp-admin`
  * `/usr/share/wordpress` -- perhaps just the whole directory tree
  * `/root/.bashrc`
  * `/root/.acme.sh`
  * the database using `mysqldump`

Maybe something like this...


```
#!/usr/bin/bash

$(return 0 > /dev/null 2>&1) && issourced=1 || issourced=0
if [ "$EUID" -ne 0 ]
  then echo "Please run with root priviledges"
  (( $issourced )) && return 1 || exit 1
fi

# As root...
_datef=$(date +%F)
_sitename=blog.example.com
_histfile=$HISTFILE ; unset HISTFILE
_dbuser=sqluser
_dbname=examplewpdb
# ..._dbpass is not used if mariadb is set to ignore scripted passwords
_dbpass='my password here, maybe, see above comment'
export HISTFILE=$_histfile

rm -rf $_sitename-$_datef ; mkdir $_sitename-$_datef
cd $_sitename-$_datef

echo "Database"
# FYI: mariadb/mysql disallows commandline passwords, so... prompted
# To restore: mysql -u $_dbuser -p < [/path/to/database/backup/]$_dbname.sql
mysqldump -u $_dbuser -p $_dbname > ./$_dbname.sql
if (( "$?" != 0 )) ; then
  echo "Caught an error. Exiting."
  cd .. ; rm -rf $_sitename-$_datef
  (( $issourced )) && return 1 || exit 1
fi
echo "DB password is good and we are backed up to $(pwd)/${_dbname}.sql"
sleep 2

echo "Configuration"
cp -a /etc/php.ini ./etc_php.ini
cp -a /etc/nginx ./etc-nginx
cp -a /etc/wordpress ./etc-wordpress
cp -a /etc/php-fpm.conf ./etc_php-fpm.conf
cp -a /etc/php-fpm.d ./etc-php-fpm.d
cp -a /root/.bashrc ./root_.bashrc
cp -a /root/.acme.sh ./root-.acme.sh

echo "Content"
cp -a /usr/share/wordpress ./usr-share-wordpress

# Archive it
# ...remember to store this backup somewhere AND TEST IT
cd ..
tar -cvzf $_sitename-$_datef.tar.gz $_sitename-$_datef
rm $_sitename-$_datef
if [ ! -z ${SUDO_USER + x} ] ; then
  chown $SUDO_USER:$SUDO_USER tar -cvzf $_sitename-$_datef.tar.gz
fi
echo "Backup archive created..."
ls -lh $_sitename-$_datef.tar.gz
```

Make that into a script. Use often. Test it!

### Addendum - restoring from backup...

[not written yet]

