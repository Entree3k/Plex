1: Download the latest web tools and unzip it, then remove the archive

https://github.com/ukdtom/WebTools.bundle

2: Move into the Plex config folder.

    /appdata/PlexMediaServer/Library/Application Support/Plex Media Server/Plug-ins
    
3: Unzip WebTools.bundle.zip and place the unzipped folder in your Plex Plug-ins folder

4: Restart Plex Media Server

    If you're running Plex on unRAID or in a Docker container you will need to add the ports needed for Web Tools to work.

    Now, add the port mappings for the Webtools UI to the docker container

    Go to the docker panel, click the plex icon, then "edit"
    " Add another Path, Port, Variable, Label or Device "
    Type: Port Name: Webtools port: 33400

5: Navigate to the web tools portal and login http://[Server IP]/33400

6: Login with your plex credentials.

7: Open the "Unsupported AppStore" module by clicking UAS under tools on the left navigation.

8: Enter the Github url for Trakt plugin ("https://github.com/trakt/Plex-Trakt-Scrobbler") in the box labeled "Manual installation URL" and click the "Manual Installation" button. The Gear icon will spin for a while and when it stops it should appear if you click "Installed #" on the right side.

The "Trakt.tv" plugin should appear at Plex/Web -> Channels in about one minute. (but can vary depending on the speed of your system)

If the plugin doesn't appear after waiting a few minutes: the plugin may not be installed correctly, or has crashed on startup. Please post an issue here with the latest plugin log file for support.

To configure the plugin open up Plex and go to the plugin tab in the settings
    Plex/Web -> Settings -> Plugins

9: Click the Gear icon for the new plugin in Trakt.tv and configure the settings for what you'll like or just leave it Default.

10: Go to the link at the top labeled

    Authentication PIN (visit https://trakt.tv/pin/***)
    
Once your Plex account and Trakt.tv account are linked your watch histroy on Plex should start to sync accross to Trakt.tv

If you want to create a Trakt.tv list that recommends you new movies and shows based on your watch history then check out the website

    https://couchmoney.tv/
    
From there you login in with your Trakt.tv account and it will create lists for you based on your watch history.
