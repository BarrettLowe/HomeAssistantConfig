# Home Asistant Setup and Configuration

This repository contains my configuration files for my Home Assistant installation. This document is created to serve as a broad explaination for technical recruiters interested in my skills and for anyone interested in setting up a system similar to mine. This is by no means a full representation of my skills. At work, I'm a C++/Python guy. At home I do this - very different worlds. That is to say that I have no formal training in these technologies - I have learned them on my own to create this system. Thus I probably know just enough to be dangerous...bring on the learning!

Organization of this document begins with broad technologies and drills down into individual software or hardware.

1. [Docker/Portainer](#docker)
2. [NGINX/Letsencrypt/Fail2Ban](#nginx)
3. [MQTT](#mqtt)
4. [Snapcast/Mopidy](#snapcast)
5. [Duplicati](#duplicati)
6. Hardware/Custom Devices
    * [Tasmota](#tasmota)
    * [ESPHome](#esphome)
7. Other Software
    * [OpenSprinkler](#opensprinkler)
    * [Vaccuum](#vacuum)

## <a name="docker">Docker/Portainer</a>
The system heavily relies on docker containers. The host system is a used x86_64 machine purchased cheaply off ebay. It's running Ubuntu 20.02 Server LTS. Very little is actually installed on the host and I try to keep it that way.

I utilize containers that I can find on dockerhub, github, and ones I create myself from Dockerfiles. [LinuxServerIO](https://www.linuxserver.io/) has some really great containers that they keep up to date. To keep up with the latest images, I use [Watchtower](https://github.com/containrrr/watchtower). By default, Watchtower automatically gets the latest images and restarts the containers as necessary. I like having a little more control over my updates so my watchtower instance is setup to simply email me with available updates. The emails are sent via AWS Simple Email Service. 

Containers are primarily managed using docker-compose. I tried out [portainer](https://www.portainer.io/) out of curiosity. It's got a nice frontend but I'm a command line guy at heart so now I just use it as an easy way to look at details or restart containers from my phone if needed.

## <a name="nginx">NGINX/Letsencrypt/Fail2Ban</a>
As mentioned before, I use LinuxServer images. They have a great [image](https://docs.linuxserver.io/images/docker-letsencrypt) that has what I need to reverse proxy my Home Assistant instance. My certificates get renewed automatically via letsencrypt, fail2ban provides protection, though minimial, against brute force attacks, and NGINX routes requests. 

There are a few servers on my network that I don't want to be accessible from outside my network. For those servers, NGINX limits access using the `listen` command, only listening for requests from my internal subnet. Our music system, for example, has no need to be controlled from outside our network.

## <a name="mqtt">MQTT</a>
I really like this little lightweight protocol. It's widely used and thus easy to find libraries to implement in python or for the ESP32 or ESP8266. I'm a fan! 

I use MQTT for wifi sensors and switches throughout the house but we also use it for tracking our phone locations. We have Android phones and utilize an automation app called [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm&hl=en_US) to send GPS coordinates back to Home Assistant via MQTT. Whenever our phones connect to (or disconnect from) our vehicles via bluetooth, Tasker performs this action automatically and repeats every hour. This has been quite successful and is plenty responsive for our needs. This however is not purely local and thus requires a publically available MQTT broker. For this, I use an EC2 instance running in AWS. There is a local broker on my internal network with a bridged connection to the AWS broker. This allows me only send minimially necessary MQTT data over the public internet (despite it being encrypted). 

Most of the MQTT devices in my system are running either ESPHome or Tasmota. See those sections below for more information on devices/hardware.

## <a name="snapcast">Snapcast/Mopidy</a>
[Snapcast](https://github.com/badaix/snapcast) is a great little piece of software. It allows me to stream music across my network to various speakers resulting in synchronized multi-room audio. I use raspberry pis and old android devices as clients in my kitchen, woodshop, nursery, family room, and back patio. These clients send their output to aplifiers, small bluetooth speakers, or my family room TV. The music is synchronized and it's wonderful!

There are 3 FIFOs that the snapcast server streams from. Two that we can stream to directly from Spotify and one that uses Mopidy. My instance of Mopidy runs in docker and I use the image that's prebuilt as an add-on for Home Assistant. I played around with using a custom docker image and was able to get it up and running. I realized, however, that maintenance and updates are easier using the add-on so that's what I settled on but I can rest assured that I am able to create my own if needed!

The end result of this system is that spotify can be streamed directly to one of the FIFOS and snapcast can route those FIFOs to any client/speaker in the house. The selection is done via the UI in home assistant.

## <a name="duplicati">Duplicati</a>
What good is all of this if it's not backed up? [Duplicati](https://www.duplicati.com/) is a nice little backup application. I use it to backup the non-configuration/persistent data of Home Assistant. This includes all my zigbee/zwave devices, username/password files, data history etc. Duplicati (again running in docker) performs its backups regularly, emailing me with any warnings or failures so that I can tend to them immediately. The backups are stored in AWS S3.

## <a name="tasmota">Tasmota</a>
This little bit of [software](https://tasmota.github.io/docs/) is neat. If you are not familiar, a pre-compiled binary can be flashed to an ESP32 or ESP8266 and furthermore configured via a webinterface. It's quite slick. I have used this on a few devices around my house. My favorite is my fan/light switch in the office. [This](https://www.amazon.com/Upgraded-Controller-Function-Compatible-Installation/dp/B07VMS8TRB/ref=pd_lpo_79_t_0/143-5452567-4498663?_encoding=UTF8&pd_rd_i=B07VMS8TRB&pd_rd_r=55e5b628-3c25-41d6-8dbb-0eb768a69b4b&pd_rd_w=Mxlsd&pd_rd_wg=LRW1h&pf_rd_p=7b36d496-f366-4631-94d3-61b87b52511b&pf_rd_r=VFM47Y742Y0HKZ4MYCFJ&psc=1&refRID=VFM47Y742Y0HKZ4MYCFJ) sort of device can be purchased very cheaply off of ali-express or ebay. I got one, popped it open, and began playing around. 

I expected to find an ESP8266 onboard due to it's cheap price and wifi connectivity. Althouh I did find the ESP8266, I also found some other little Cortex M1 micro. After some poking around and scoping the signal, I found that the ESP and the Cortex communitated over the ESP's default UART and that the Cortex controller was used as the controller while the ESP was simply used as a wifi sender/receiver. Tasmota has a feature called TuyaMCU. Luckily, someone had already run into this type of setup and I could simply flash tasmota on the ESP then use the device how I desired without sending data outside my network. 

After some soldering to keep the Cortex chip disabled and attach the ESP's uart to my FTDI chip, I was able to flash the software to the ESP, get it connected to my local MQTT server, and control the fan and light. Now I have a device that doesn't communicate to some unknown server and I control this device 100%. 

## <a name="esphome">ESPHome</a>
If you are not familiar with [ESPHome](https://esphome.io/), it's a package that allows you to compile embedded C code using a simple yaml file. The embedded code can run on ESP8266 and ESP32 and is pretty simple to use. There is support for a wide variety of sensor hardware. Data can either be sent directly to Home Assistant or to an MQTT broker. 

The ESP devices are great because they are versatile and cheap. I have reflashed various brands of smart plugs as well as custom made devices. The nursery has an esp8266 monitoring temperature and humidity as well as a pressure mat under the crib mattress. The garage sensor has an esp32 monitoring and controlling garage doors as well as temperature/humidity and a PIR motion sensor. ESPHome makes for easy setup and allows a little bit of abstraction when sensors have common configurations (MQTT and Wifi for example). My ESPHome configuration repository is located [here](https://github.com/BarrettLowe/esphome-config) for reference.

## <a name="opensprinkler">OpenSprinkler</a>
This barely warrants its own section. [OpenSprinkler](https://opensprinkler.com/) is an open source sprinkler controller that runs on a raspberry pi. It's installed on the pi in my woodshop as that's where the sprinkler wires run. The Pi is hooked up to a 12 channel relay to switch individual stations on and off. It works great! It integrates with Home Assistant thus gets its schedule adjusted based on the amount of rain we've gotten. It's accessible as a subdomain to my externally facing domain I use to access Home Assistant from the rest of the world but NGINX only listens to internal requests. Unless you're on my network, you can't control the irrigation.

## <a name="vacuum">Vacuum</a>
Our vacuum is a Roborock S5. The [Valetudo](https://github.com/Hypfer/Valetudo) software runs ontop of the standard application allowing me to control and monitor the vacuum over MQTT. I can also ssh into the vacuum if I really want to tinker. Every day, the vacuum cleans 2 rooms. After it has completed its cleaning, Home Assistant commands it to drive to the trashcan and wait for us to empty the dustbin. By the end of the week, it has hit every room. This sequence of actions makes sure the whole house is vacuumed every week and that the dustbin gets emptied between runs.