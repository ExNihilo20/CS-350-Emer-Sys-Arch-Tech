#
# Milestone3.py - This is the Python code template used to 
# setup the structure for Milestone 3. In this milestone, you need
# to demonstrate the capability to productively display a message
# in Morse code utilizing the Red and Blue LEDs. The message should
# change between SOS and OK when the button is pressed using a state
# machine.
#
# This code works with the test circuit that was built for module 5.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

##
## Imports required to handle our Button, and our LED devices
##
from gpiozero import Button, LED

##
## Imports required to allow us to build a fully functional state machine
##
from statemachine import StateMachine, State

##
## Import required to allow us to pause for a specified length of time
##
from time import sleep

##
## These are the packages that we need to pull in so that we can work
## with the GPIO interface on the Raspberry Pi board and work with
## the 16x2 LCD display
##
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

from threading import Thread

##
## DEBUG flag - boolean value to indicate whether or not to print 
## status messages on the console of the program
## 
DEBUG = True

##
## ManagedDisplay - Class intended to manage the 16x2 
## Display
##
class ManagedDisplay():
    ##
    ## Class Initialization method to setup the display
    ##
    def __init__(self):
        ##
        ## Setup the six GPIO lines to communicate with the display.
        ## This leverages the digitalio class to handle digital 
        ## outputs on the GPIO lines. There is also an analagous
        ## class for analog IO.
        ##
        ## You need to make sure that the port mappings match the
        ## physical wiring of the display interface to the 
        ## GPIO interface.
        ##
        ## compatible with all versions of RPI as of Jan. 2019
        ##
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)

        # Modify this if you have a different sized character LCD
        self.lcd_columns = 16
        self.lcd_rows = 2 

        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, 
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, 
                    self.lcd_columns, self.lcd_rows)

        # wipe LCD screen before we start
        self.lcd.clear()

    ##
    ## cleanupDisplay - Method used to cleanup the digitalIO lines that
    ## are used to run the display.
    ##
    def cleanupDisplay(self):
        # Clear the LCD first - otherwise we won't be abe to update it.
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()
        
    ##
    ## clear - Convenience method used to clear the display
    ##
    def clear(self):
        self.lcd.clear()

    ##
    ## updateScreen - Convenience method used to update the message.
    ##
    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

    ## End class ManagedDisplay definition  
    

##
## CWMachine - This is our StateMachine implementation class.
## The purpose of this state machine is to send a message in 
## morse code, blinking the red light for a dot, and the blue light
## for a dash.
##
## A dot should be displayed for 500ms. 
## A dash should be displayed for 1500ms.
## There should be a pause of 250ms between dots/dashes.
## There should be a pause of 750ms between letters.
## There should be a pause of 3000ms between words.
##
class CWMachine(StateMachine):
    "A state machine designed to display morse code messages"

    ##
    ## Our two LEDs, utilizing GPIO 18, and GPIO 23
    ##
    redLight = LED(18)
    blueLight = LED(23)

    ##
    ## Set the contents of our messages
    ##
    message1 = 'SOS'
    message2 = 'OK'

    ##
    ## keep track of the active message
    ##
    activeMessage = message1

    ##
    ## endTransmission - flag used to determine whether or not
    ## we are shutting down
    ##
    endTransmission = False

    ##
    ## Define these states for our machine.
    ##
    ##  off - nothing lit up
    ##  dot - red lit for 500ms
    ##  dash - blue lit for 1500ms
    ##  dotDashPause - dark for 250ms
    ##  letterPause - dark for 750ms
    ##  wordPause - dark for 3000ms
    ##
    off = State(initial = True)
    dot = State()
    dash = State()
    dotDashPause = State()
    letterPause = State()
    wordPause = State()

    ##
    ## Initialize our display
    ##
    screen = ManagedDisplay()

    ##
    ## A dictionary of Morse Code - this is a utility that will allow us
    ## to convert any common string into Morse code.
    ##
    morseDict = {
        "A" : ".-", "B" : "-...", "C" : "-.-.", "D" : "-..",
        "E" : ".", "F" : "..-.", "G" : "--.", "H" : "....",
        "I" : "..", "J" : ".---", "K" : "-.-", "L" : ".-..",
        "M" : "--", "N" : "-.", "O" : "---", "P" : ".--.",
        "Q" : "--.-", "R" : ".-.", "S" : "...", "T" : "-",
        "U" : "..-", "V" : "...-", "W" : ".--", "X" : "-..-",
        "Y" : "-.--", "Z" : "--..", "0" : "-----", "1" : ".----",
        "2" : "..---", "3" : "...--", "4" : "....-", "5" : ".....",
        "6" : "-....", "7" : "--...", "8" : "---..", "9" : "----.",
        "+" : ".-.-.", "-" : "-....-", "/" : "-..-.", "=" : "-...-",
        ":" : "---...", "." : ".-.-.-", "$" : "...-..-", "?" : "..--..",
        "@" : ".--.-.", "&" : ".-...", "\"" : ".-..-.", "_" : "..--.-",
        "|" : "--...-", "(" : "-.--.-", ")" : "-.--.-"
    }

    ##
    ## doDot - Event that moves between the off-state (all-lights-off)
    ## and a 'dot'
    ##
    doDot = (
        off.to(dot) |
        dash.to(dot) | 
        dotDashPause.to(dot) |
        letterPause.to(dot) |
        dot.to(off)
    )

    ##
    ## doDash - Event that moves between the off-state (all-lights-off)
    ## and a 'dash'
    ##
    doDash = (
        off.to(dash) |
        dot.to(dash) | 
        dotDashPause.to(dash) |
        letterPause.to(dash) |
        dash.to(off)
    )

    ##
    ## doDDP - Event that moves between the off-state (all-lights-off)
    ## and a pause between dots and dashes
    ##
    doDDP = (
        dot.to(dotDashPause) |
        dash.to(dotDashPause) |
        off.to(dotDashPause) |
        dotDashPause.to(off)
    )


    ##
    ## doLP - Event that moves between the off-state (all-lights-off)
    ## and a pause between letters
    ##
    doLP = (
        dot.to(letterPause) |
        dash.to(letterPause) |
        dotDashPause.to(letterPause) |  # optional, if it can happen after dot-dash pause
        off.to(letterPause) |           # optional, if off state might also lead into letterPause
        letterPause.to(off)
    )

    ##
    ## doWP - Event that moves between the off-state (all-lights-off)
    ## and a pause between words
    ##
    doWP = (
        off.to(wordPause) | wordPause.to(off)
    )

    ##
    ## on_enter_dot - Action performed when the state machine transitions
    ## into the dot state
    ##
    def on_enter_dot(self):
        # Red light comes on for 500ms
        self.redLight.on()  # Turn on red LED for dot
        sleep(0.5)  # 500ms for dot
        self.redLight.off()  # Turn off the red LED

        if(DEBUG):
            print("* Changing state to red - dot")

    ##
    ## on_exit_dot - Action performed when the statemachine transitions
    ## out of the red state.
    ##
    def on_exit_dot(self):
        # Red light forced off
        self.redLight.off()  # Turns the red LED off

    ##
    ## on_enter_dash - Action performed when the state machine transitions
    ## into the dash state
    ##
    def on_enter_dash(self):
        # Blue light comes on for 1500ms
        self.blueLight.on()  # Turn on blue LED for dash
        sleep(1.5)  # 1500ms for dash
        self.blueLight.off()  # Turn off the blue LED

        if(DEBUG):
            print("* Changing state to blue - dash")

    ##
    ## on_exit_dash - Action performed when the statemachine transitions
    ## out of the dash state.
    ##
    def on_exit_dash(self):
        # Blue light forced off
        self.blueLight.off()  # Turns the blue LED off

    ##
    ## on_enter_dotDashPause - Action performed when the state machine 
    ## transitions into the dotDashPause state
    ##
    def on_enter_dotDashPause(self):
        # wait for 250ms
        sleep(0.25)  # Pause for 250ms between dots and dashes
        if(DEBUG):
            print("* Pausing Between Dots/Dashes - 250ms")

    ##
    ## on_exit_dotDashPause - Action performed when the statemachine transitions
    ## out of the dotDashPause state.
    ##
    def on_exit_dotDashPause(self):
        if(DEBUG):
            print("* Exiting Dot-Dash Pause")

    ##
    ## on_enter_letterPause - Action performed when the state machine 
    ## transitions into the letterPause state
    ##
    def on_enter_letterPause(self):
        # wait for 750ms

        ## TODO: Add the single line of code necessary to pause execution
        ## of the next operation for 750ms. Remove this TODO comment block when
        ## complete.
        sleep(0.75)  # Pause for 750ms between letters
        if(DEBUG):
            print("* Pausing Between Letters - 750ms")

    ##
    ## on_exit_letterPause - Action performed when the statemachine transitions
    ## out of the letterPause state.
    ##
    def on_exit_letterPause(self):
        if(DEBUG):
            print("* Exiting Letter Pause")
        

    ##
    ## on_enter_wordPause - Action performed when the state machine 
    ## transitions into the wordPause state
    ##
    def on_enter_wordPause(self):
        # wait for 3000ms
        
        ## TODO: Add the single line of code necessary to pause execution
        ## of the next operation for 3000ms. Remove this TODO comment block 
        ## when complete.
        sleep(3)  # Pause for 3000ms between words
        if(DEBUG):
            print("* Pausing Between Words - 3000ms")

    ##
    ## on_exit_wordPause - Action performed when the statemachine transitions
    ## out of the wordPause state.
    ##
    def on_exit_wordPause(self):
        if(DEBUG):
            print("* Exiting Word Pause")
        

    ##
    ## toggleMessage - method used to switch between message1
    ## and message2
    ##
    def toggleMessage(self):
        if self.activeMessage == self.message1:
            self.activeMessage = self.message2
        else:
            self.activeMessage = self.message1

        if(DEBUG):
            print(f"* Toggling active message to: {self.activeMessage} ")

    ##
    ## processButton - Utility method used to send events to the 
    ## state machine. The only thing this event does is trigger
    ## a change in the outgoing message
    ##
    def processButton(self):
        print('*** processButton')
        self.toggleMessage()

    ##
    ## run - kickoff the transmit functionality in a separate execution thread
    ##
    def run(self):
        myThread = Thread(target=self.transmit)
        myThread.start()
        
    ##
    ## transmit - utility method used to continuously send a
    ## message
    ##
    def transmit(self):

        ##
        ## Loop until we are shutdown
        ##
        while not self.endTransmission:

            ## Display the active message in our 16x2 screen
            self.screen.updateScreen(f"Sending:\n{self.activeMessage}")

            ## Parse message for individual wordsTAM
            wordList = self.activeMessage.split()

            ## Setup counter to determine time buffer after words
            lenWords = len(wordList)
            wordsCounter = 1
            for word in wordList:
            
                ## Setup counter to determine time buffer after letters
                lenWord = len(word)
                wordCounter = 1
                for char in word:

                    ## Convert the character to its string in morse code
                    morse = self.morseDict.get(char)

                    ## Setup counter to determine time buffer after letters
                    lenMorse = len(morse)
                    morseCounter = 1
                    for x in morse:

                        ## Dot or dash?
                        if x == '.':
                            self.doDot()  # Transition to dot state
                        elif x == '-':
                            self.doDash()  # Transition to dash state

                        
                        # If we are still sending process a dotDashPause event
                        if morseCounter < lenMorse:
                            if self.current_state == self.dot:
                                print("it's a dot")
                            if self.current_state == self.dash:
                                print("it's a dash")
                            if(DEBUG):
                                print(f"Current State: {self.current_state}, Processing: {x}")
                        # Transition to the pause state only if we're in the dot or dash state
                            if self.current_state == self.dot or self.current_state == self.dash:
                                print('inside dot or dash')
                                if(DEBUG):
                                    print(f"Current State: {self.current_state}, Processing: {x}")
                                self.doDDP()  # Pause between dots and dashes
                        morseCounter += 1

                    # If we are still sending process a letterPause event
                    if wordCounter < lenWord:
                        self.doLP()  # Pause between letters
                    wordCounter += 1
                # If we are still sending process a wordPause event

                if wordsCounter < lenWords:
                    self.doWP()  # Pause between words
                wordsCounter += 1
        ## Cleanup the display i.e. clear it
        self.screen.cleanupDisplay()



    ## End class CWMachine definition


##
## Initialize our State Machine, and begin transmission
##
cwMachine = CWMachine()
cwMachine.run()

##
## greenButton - setup our Button, tied to GPIO 24. Configure the
## action to be taken when the button is pressed to be the 
## execution of the processButton function in our State Machine
##
greenButton = Button(24)

greenButton.when_pressed = cwMachine.processButton
##
## Setup loop variable
##
repeat = True

##
## Repeat until the user creates a keyboard interrupt (CTRL-C)
##
while repeat:
    try:
        ## Only display if the DEBUG flag is set
        if(DEBUG):
            print("Killing time in a loop...")

        ## sleep for 20 seconds at a time. This value is not crucial, 
        ## all of the work for this application is handled by the 
        ## Button.when_pressed event process
        sleep(20)
    except KeyboardInterrupt:
        ## Catch the keyboard interrupt (CTRL-C) and exit cleanly
        ## we do not need to manually clean up the GPIO pins, the 
        ## gpiozero library handles that process.
        print("Cleaning up. Exiting...")

        ## Stop the loop
        repeat = False
        
        ## Cleanly exit the state machine after completing the last message
        cwMachine.endTransmission = True
        sleep(1)