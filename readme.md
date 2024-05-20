
# AttMan - Racing League Attendance Manager

Recently the Discord Bot "GridMaker" was taken offline for reasons unknown. Whilst there are other event management bots available, it is clear that many users relied on "GridMaker" to manage their leagues.

To help somewhat bridge the gap, this bot has been created specifically for a small number of leagues to replicate the functionality they used before.



## Installation

Prior to installation, the following files will need to be renamed:

``` bash
sudo mv ./resources/.env-template ./resources/.env
sudo mv ./config/servers-template.json ./config/servers.json
```

Edit the .env file to add your bot token, and optionally Open AI key if you require track descriptions on your attendance posts

``` bash
sudo nano ./resources/.env
```

Install using docker compose

```bash
sudo docker compose up -d
```
    
## Usage

The bot works on a server and league configuration and should be run in the following order

/register - to add your server details to servers.json

/add_league - to add your league name to your server configuration

/configure_league - to add tags, roles and schedule to your league

/add_event - to select the league and track for your league

The bot will calculate the next event for your league based on the schedule configuration.

Track list is predefined and editable in ./config/tracks.json - bearing in mind the 25 item limit in Discord select lists.

./config/stored_values.json is a workaround to create a league configuration as I haven't yet figured out how to pass previous responses between functions

WORK IN PROGRESS!


