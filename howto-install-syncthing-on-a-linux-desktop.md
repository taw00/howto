# HowTo Install Syncthing on a Linux Desktop

## Let's do it!

Getting Syncthing up and running on a linux desktop is SUPER pain free.

0. **Login to your desktop as a normal user**

1. **Install `syncthing` and `firewalld` and the _Syncthing Tray_ system tray utility**

```bash
sudo dnf install syncthing firewalld -y
flatpak install io.github.martchus.syncthingtray -y
```

2. **Configure `firewalld` to allow communication with the `syncthing` service**

For more expansive info about firewalld (and fails2ban): <https://github.com/taw00/howto/blob/master/howto-configure-firewalld-and-fail2ban-for-linux.md>

```bash
# Turn on and enable firewalld if not already done...
sudo firewall-cmd --state
sudo systemctl start firewalld.service
sudo systemctl enable firewalld.service

# If you had custom zoning set, remember to add --zone=<yourzonelabel> to the
# configuration commands, though if the zone is configured to be the default,
# things should "just work"
sudo firewall-cmd --get-active-zones
#sudo firewall-cmd --zone=<yourzonelabel> --list-all
#sudo firewall-cmd --list-all

# allow the syncthing service, but DO NOT allow the GUI service to be exposed
# to the internet. You don't need that added exposure.
sudo firewall-cmd --add-service=syncthing --permanent
#sudo firewall-cmd --add-service=syncthing-gui --permanent
sudo firewall-cmd --reload
```


3. **Enable the `syncthing` service and start it up**

```bash
syncthing --user enable syncthing.service
syncthing --user start syncthing.service
```

Configuration and whatnot will, by default, live in `$HOME/.local/state/syncthing/`

4. **Browse to <http:127.0.0.1:8384> and configure your instance**

Read the docs! <https://docs.syncthing.net/> Once you have a set username and password and you are happy with your setup …

5. **Run the Syncthing Tray application**

In your desktop interface, find the _Syncthing Tray_ application, and run it. Select these options in the wizard that will pop up …

- Start guided setup
- Configure Syncthing Tray for currently running Syncthing instance
- Next
- Apply
- Copy that ID somewhere (it's also in the webui)
- Finish

Done. You should now see a little Syncthing icon in your system tray if you have that enabled. If you don't see it, you may have to enable the visibility of system tray icons. On GNOME, you do that with the [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/) GNOME Extension. I recommend installing that. Note that you may have to use Firefox to install extensions. I don't know. That is beyond the scope of this document.

If you screw up the Syncthing Tray set up, it is easiest to uninstall it, then start over with the wizard configuration. You will have to uninstall it _and_ quit the icon in the system tray (click on it and select quit).

FYI. The Syncthing Tray application is only useful as an service-wellness barometer. Otherwise it doesn't do much. You can also kick open the webUI with it as well. The color will be green if the `syncthing` service is running okay and it will some other color if something seems to be amiss.

Done! Now follow the docs for using the service: https://docs.syncthing.net/ Set Syncthing up on all of your systems and share files and documents between them.

---

## Good luck!

Comments and feedback to <t0dd@protonmail.com>

