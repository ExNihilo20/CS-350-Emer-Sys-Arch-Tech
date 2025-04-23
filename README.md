# Final Project

## Project Summary
This course gave students practice working with embedded systems. Over the past 8 weeks, we have completed iterations of a programmable thermostat. The project included the following peripherals:
- Buttons
- LEDs
- resistors
- rheostat
- jumper wires
- bread board
- AHT20 temp and humidity sensor
- GPIO cabling
- ribbon cable
- Raspberry Pi 4

Be the course's end, we had a programmable thermostat that responded to button input. We programmed:
1. A green button to move between heat, cool, and off states. 
2. A blue button to lower the temperature set point.
3. A red button to raise the temperature set point.

The thermostat is programmed in Python. When in HEAT mode, the red LED will blink if the temperature is below the set point. Once the set point is reached, the LED will shine solid red. Similarly, the blue LED will blink when in cooling mode if the temperature is below the set point. Once the temperature meets the set point, the blue LED will shine solid blue. In off mode, neither LED illuminates.

## Project Highlights
While this project was challenging, we were given a chance to explore IoT applications and learn how to connect software systems to external hardware. The breadboard was a great learning experience, and I appreciate the prototyping that is possible on a non-soldered board. We were able to easily add or remove jumper wires, resistors, switches, and more until we achieved our desired circuit.

## Areas for Improvement
I would like to have a GUI dashboard to run the project from. Our project executed Python code directly from a Linux server command line. Ideally, we would have a GUI that would interface with the server and would have executable programs that we could call for our convenience. Regardless, we still got experience with SSH (connecting to our server), setting up Ubuntu server on the Raspberry Pi, and more.

## Tools and Resources Gained
The course strengthened core capabilities in Python programming, linux system administration, deploying code to a server securely via SSH, setting up a remote server, integrating everything through a controller (Raspberry Pi), and more. We are now positioned to build on this knowledge base and create more functional and dynamic systems to suit both personal and professional needs. 

## Transferrable Skills
Some of the transferrable skills are as follows:
- Network Administration
- Circuit Design
- Python Programming
- Embedded Development
- Project Planning
- Project Diagramming
- Project Reporting

## Project Maintainability, Readability, Adaptability
The project was created with descriptive variable, function, and class names to self-document programmatic execution. We embedded comments in the Python program to aid in understanding control flow and runtime execution of the software. To add to this, each student created diagrams to accompany the projects to show critical steps and program states during execution.
