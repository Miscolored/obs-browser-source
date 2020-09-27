A full-on OBS score tracking script.

The script deploys a local web-app that shows the score (for use as an OBS browser source). Clicking a score updates them across all browsers (includign the OBS browser source). With this, you can update your score for your viewers in real time using any android, iphone, computer, or tablet on the OBS-computer network.

# Usage
1. Once deployed, the script launches a containerized webapp that can be used to control the score shown
1. Use a web browser to increment or reset scores based on your wins/losses in all kinds of games, like Among Us, CSGO, etc.

# Install/Deploy
## Prerequisites
1. Windows 10 (tested on 1909 build 18363.1082, Linux/MacOS users should be fine with similar prereqs))
1. Python 3.6 (tested on 3.6.7)
1. Docker (tested on 19.03.12)
1. OBS (tested on OBS Studio 25.0.8)

## Start the score-card plugin
1. Clone or download the contents of this repo
1. Open OBS Tools>Scripts>+
1. Select score-card-obs-script.py
1. Add Scores To Track appropriate for your game (i.e. crew, impostor or cops, robbers)
1. Select Fonts, and Colors (note the Score Font options are your system fonts, and may not render as expected across devices (including your OBS browser source))
1. Click Deploy Score Card Server

## Adding the scorecard as an overlay in OBS
1. Once deployed, create a new browser source with the following information
  * Local file, Use customer frame rate, Control audio via OBS, Shutdown source when not visible: uncheck
  * Refresh browser when scene becomes active: check
  * URL:  http://localhost/5000/score-card
  * Width: depends on your game, font, score names, and stream resolution (400 is a good starting point)
  * Height: depends on your game, font, number of scores, and stream resolution (175 is a good starting point)
  * Click Refresh cache of current page
1. The score card is now available as a browser source to be added to your OBS scenes

## Updating the scores
You cannot interact with the browser source from your OBS scene. You must use a browser on the OBS host or other browsing device on the same network.

### Viewing the app locally (on OBS host)
1. Browser to http://localhost:5000/score-card/
1. Click the win and loss cells to update the scores

### Viewing the app on another device (ios, android, laptop, etc)
1. Ensure the devices are connected to the same network
1. Obtain the _internal network_ IP address of OBS host (typically start with 172 or 192) (use ifconfig, ipconfig, ipaddr depending on host OS, or google)
1. On the other device, browse to http://<OBS HOST IP>:5000/score-card

## Shutting down and cleaning up
1. From OBS Scripts window, select score-card-obs-script.py
1. Click Remove Score Card Server (this will delete the container and image created during deployment)

# Logs
The plugin writes some log information to the OBS log, which can be accessed through OBS via Help>Log Files>View Current Log
The app writes some log information to a logfile on the container called score-card.log, which can be accessed through `docker exec -it score-card cat score-card.log`

# Troubleshooting
**Host not found or 404 errors when accessing score-card app (local)**
1. Check if the docker container is running, from command line type `docker ps` and ensure score-card is running
1. Check that you have added the port number to the URL (5000 is default for the app)

**Scores not updated when clicked**
1. The webapp uses javascript, sockets, and jquery. It is possible your browser settings are blocking some of this functionality.
1. The score-card container my have been terminated.

# Bugs and Features
Open an issue if you'd like me to add a feature or fix a bug.
Open a PR if you've added or fixed something, or just fork.

# Future Roadmap Ideas
1. Add ties
1. Load saved configurations
1. Create browser source
  1. Tailor browser source based on configuration
1. Alexa integration
1. Cloud hosting
1. Persistent (i.e. all-time) scores