## Intelligent home system

### List of content
1. **Preview**
2. **Purpose**
2. **Hardware**
3. **Software**
4. **System in action**
4. **Installation**
5. **Conclusion**

### Preview

In this manual I will describe intelligent home system which I have to developed. It is based on Raspberry Pi which serves as web server and logic master. All system functions are provided by Atmega slave boards. I will briefly explain how the hardware works. Later on main software concepts will be shown. At the beginning I would like to emphasis that I will be extremely happy if somebody would like to cooperate with me on the project. I can supply you with the hardware needed :)

| System hardware | House maquette |
| :-------: | :-------: |
| ![](https://s31.postimg.org/zb6s8yqbt/system.jpg) | ![](https://s31.postimg.org/gucdi5adn/maquette.jpg) |


### Purpose

Purpose of project is to build intelligent home system which is reliable, scalable, modifiable and cheap. In my opinion reliability can by only achieved by using wired network between system nodes. Modular topology gives scalability as you can easily extend system by adding extra modules. I did my best to write simple understandable and modular Pythonic code so it would be easy to modify operation of the system. Talking about cost it is widely known that RPi is a cheap computer (about 20$). Same goes with slave boards for which production price oscilates between 30-50$ depending on the board.

### Hardware

Core of the system is widely known [Raspberry Pi](https://www.raspberrypi.org/) computer (_it basically may be any other linux or windows computer_). It is connected with Atmega based boards (which I have developed) by RS485 twisted pair cable. RPI serves as web server and logic master. It is connected with the internet to handle traffic from clients to system and vice versa. It also sends and reads modbus messeges to and from slaves.

For the present time i have developed 5 different slaves boards. All are based on [Atmega328](https://en.wikipedia.org/wiki/ATmega328) micro controller which can be found in [Arduino](https://www.arduino.cc/). They can be powered from 10V-24V AC/DC. All of the communicate via RS485 physical interface.  All boards have top board with TX and RX leds indicating communication and pulsating RGB led indicating board status.

These are:
* **Output board**  
Purpose of output board is to turn on and off electric appliances. It is equipped with 10 relays so it can control 10 devices. In addition, the board has special top with 10 leds each indicating state of corresponding relay.

| Output board | Output board top |
| :-------: | :-------: |
| ![](https://s31.postimg.org/99a9pbicr/DSC_0351.jpg) | ![](https://s31.postimg.org/nm3pnn2cr/DSC_0357.jpg) |

* **Input board**  
Purpose of input board is to get states of on/off devices such as Reed switches, switches, PIR sensors, smoke sensors. This board is in prototype state and was made as RPI shield
* Led light board  
Purpose of led light board is to dim DC appliances. Most often it would be LED stripes. It has got 3 channels controlled by mosfet transistors. Voltage can be regulated from 0 to 100% by the PWM.

| Led light board |
| :-------: | 
| ![](https://s31.postimg.org/5gqr9l2uj/DSC_0355.jpg) |

* **Ambient board**  
Purpose of ambient board is to gather information from sensors. Currently the board supports ds18b20 temperature sensors DHT22 humidity and temperature sensors, BMP180 pressure and temperature sensor, and analog sensors such as fotoresistors for light level measure.

| Ambient board |
| :-------: | 
| ![](https://s31.postimg.org/3mdwrufu3/DSC_0352.jpg) |

* **Glow light board** - (_Not used in project_)  
The board is very similar to Led light. Rather than DC it controls AC voltage by firing Triacs. It has got 3 channels so for example 3 glow bulbs can be dimmed.

| Glow light board |
| :-------: | 
| ![](https://s31.postimg.org/ni9w7dwvf/DSC_0354.jpg) |


### Software

Code consists of 3 main modules. These are backend, server and client. This graph explains relations between software modules and system. 

![System topology](https://s32.postimg.org/kurfgqjtx/General.jpg)

There is also configuration script which populate database with all necessary data

#### Language
I have chosen **Python** language to implement system logic and server. Client code is implemented in **javascript/html/css**.

#### Terminology.
I will now explain terminology used in system. It will give you a basic glance at system operation principal.

System is made from __components__. These are:

* **Elements** - all input and output devices connected to system. For example, sensors, switches, lights, heaters etc.
* **Modules** - Boards that are connected to RS485 net.
* **Relations** - Relations between elements. I have implemented two types of relations: 
  * Regulations. They control output element based on feed element value to maintain set value. ```Turning on and off heater to maintain desired temperature```
  * Dependencies. They consist of cause and effects. If the cause is evaluated to true, then effects happen in desired time after cause.   
```When light level is less than 20% and soil humidity less than 30% then turn on soil irrigation (Evening irrigation)```
* **Rooms** - House rooms. For now, purpose of room is only visual. They store reference to elements that are in the room. It allows to display system topology in client application.
* **Groups** Also visual purpose. They aggregate elements with similar functions. For example, heating group aggregates temperature sensor, heater and temperature regulation set.


#### Client application

![](https://s32.postimg.org/4v6dr7hqt/client.jpg)

For the present moment client view is very simple. Its purpose is to display all elements organized in groups and rooms. Client layout is generated by server. Js code is responsible for authorization, communication and system values update. In future I would like to improve client side in such way that server will send only representation of system - (elements id's, types and relations between elements). Client would then generate view by itself.

#### Server application
As a server i have used [Tornado webserver](http://www.tornadoweb.org/en/stable/). It is lightweight fast and easy to use server. It supports websockets which are the way to exchange information between clients and system in the real time. Server's responsibilities are:
* Authorization of users
* Generation of visual system structure (In the future i plan to pass this task to client code)
* Exchanging information between clients and logic. 

#### Backend application
Backend consist of three main threads. These are:
* Communication thread - Holds websocket connection. It listens to server incoming transmission and sends messages to server which are generated by logic thread.
* Logic thread - Takes care of evaluation of relations in system and checks messages from communication process. If any relations evaluate to true or there are commands to be done from clients it creates task list which is passed to modbus thread. It also checks element's "new_value_flag" which are set by modbus thread whenever any element has new value. If so then appropriate message is passed to communication thread buffer.
* Modbus thread - It is responsible for communication with slave boards. It polls all input boards as fast as it can. It is important to achieve low response latency. If there are any tasks to be done appropriate message is sent to output boards.

#### Configuration script
In the script you can define system. First you should add all the modules connected to network and rooms in your apartment.
Then you can add as many input and output elements as you want, specifying to which module are they connected and in which room are they placed. At the end you define regulations and dependencies between elements.


### System in action!

Video presents operation of system: https://www.youtube.com/watch?v=Z7VvjViKQB0&feature=youtu.be

### Installation

System can be installed on linux and windows machines. Server and client application can be run without any additional hardware. If you would like to run backend you are going to need Arduino to emulate system board. I will now write down all steps starting with Server. If you have any problems, please let me know.

**Common steps:**

1. First of all you need to install [python 3.5](https://www.python.org/downloads/)
2. Then install pip for easy packages installation. On Linux just type  
```sudo apt-get install pip3.5```On windows: [tut](http://stackoverflow.com/questions/4750806/how-do-i-install-pip-on-windows)
3. Install packages used in project:  
```sudo pip3.5 install pyserial websocket-client coloredlogs tornado dominate```
4. All imports statements in the code are relative to system directory. To make python see this directory as environment directory you should add ```system.pth``` file in site-packages directory. you can find the directory by typing in python shell:  
```import site site.getsitepackages()```

**Config steps:**

1. In your favorite code editor open system/backend/config/config.py. The file contains factory class for creating system. At the bottom you can see example configuration and explanation on how to configure system
2. Run config and create database located at system/backend/sys_database/sys_database.db . Of course you can use default configuration which is already in database supplied.

**Server steps:**

1. With the console open navigate to system/server_client and type python3 start.py (_insure that you have python3 in your system path_)
2. Script should run and it is going to show that rooms were loaded 
3. Go to your browser and type: localhost:8888. You should see client view.

**Backend steps:**

1. First of all you are going to need Arduino with modbus slave code. You can find slave modbus library [here](https://github.com/angeloc/simplemodbusng).
2. Example code for input board with id 1 that will set input states to on or off [here](http://pastebin.com/J806GX8q).
3. in ```system/backend/modbus/modbus.py``` in ```Modbus``` class change serial port so it matches your Arduino's port.
3. With the console open navigate to ```system/backend``` and type ```python3 start.py```
4. Go to the browser and you should see half of inputs on and half of them off.
5. You can turn on debugging by going to ```system/backend/start.py``` and setting loggers level to ```DEBUG```.

### Conclusion
Currently project is in working but still very early stage. I have a lot of ideas how to make the system better. For example: 
* It would be awesome to make new gui rendered by the client. 
* A proper gui configuration tool would be great to have.
* Graphs for ambient readings.
* Module for configuration slave boards f. example dim time for led light board or types of connected device for input board so it knows how to deal with them rather than simply returning 1 or 0 corresponding to on and off.

If you would like to cooperate with me on system development, I would be very pleased. I can support with the hardware needed as I have got few additional boards. Please contact me with any questions via email: _janpleszynski@gmail.com or simply on Facebook: _https://www.facebook.com/jan.pleszynski remove trailing _ .
