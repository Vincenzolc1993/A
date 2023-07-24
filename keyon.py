##########################################################################################################
#  RAFAEL CAMPAGNOLI, NICOLA STIAVELLI: last update: 20230721                                            #
#                                                                                                        #
#  IPC Test Automation Management: Keyon script using Python CAN library to perform a whole automated    #
#  test case from "key on" to speed setting and turning arrows activation.                               #
#  The signal are directly sent from the Python script to the IPC via CAN case connection w/out          #
#  passing through CANalyzer application.   
#
#  The name of the messages, signals, ID etc. are retrieved with CANtools Python library from the        #
#  .dbc files.                                                                                           #
#                                                                                                        #
#                                                                                                        #
#                                                                                                        #
#                                                                                                        #
##########################################################################################################

import easyocr
import cantools
import can
from pprint import pprint
from can.interfaces import vector
import cv2
import time

# Dictionaries to import the singnals names and values from the .dbc files and the following encodings
ignData = {}
extData = {}
engineData = {}
brakeData = {}

# Assign to each can Bus a channel already assigned in the Vector CAN manager application: CAN 1-> CAN C1
# CAN 2 -> CAN BH. Remember the numeration for python can library starts from 0 so: channel = 0 == CAN 1(CAN C1) 
# == real can channel on the can case channel 2.
can_c1 = can.interface.Bus(channel=0, bustype='vector',bitrate = 500000) # First channel, Hardware interface is
# the Vector can case and the bit rate for each channel. # call it bus_can_c1!!
can_bh = can.interface.Bus(channel=1, bustype='vector',bitrate = 125000) # Second channel, Hardware interface is
# the Vector can case and the bit rate for each channel. # call it bus_can_bh!!

# Select the camera(usb one) and assigning it the variable
cam_port = 0
cam = cv2.VideoCapture(cam_port)

'''
file = open('updates.txt', 'w')
while True:
    message = can_c1.recv()
    file.write(str(message)+'\n')
    #print(message)
    if cv2.waitKey(0) & 0xFF == ('q'):
        break

can_c1.shutdown()
file.close()
'''
# Assignment and loading of files for each database in the network
db = cantools.database.load_file(r'C:\Users\DJ0PWPX.AUDI\Desktop\ALTEN\IPC\P637MCA_C1-CAN_E2A_R1_plus_CR16083.dbc')
dbb = cantools.database.load_file(r'C:\Users\DJ0PWPX.AUDI\Desktop\ALTEN\IPC\P637MCA_BH-CAN_E2A_R1_plus_CR16663.dbc')

# Select the language for the text interpretation
reader = easyocr.Reader(['en'], gpu = False)

# Retrieving the messages from the databases with their main infos(ID, Signals, Values, Lenght)
BCM_COMMAND = db.get_message_by_name('BCM_COMMAND')
ENGINE1 = db.get_message_by_name('ENGINE1')
EXT_LIGHTS = dbb.get_message_by_name('EXTERNAL_LIGHTS')
BRAKE1 = db.get_message_by_name('BRAKE1')

# Create dictionaries with all the signals for each message
ignList = BCM_COMMAND.signal_tree
extLightsList = EXT_LIGHTS.signal_tree
engine1list = ENGINE1.signal_tree
brakelist = BRAKE1.signal_tree

# Fill the dictionaries for each message with its own signals and setting all to zero(try: signal.initial() to
# set the initial value)
for el in ignList:
    ignData[el]=0 # change'0' with signal.initial to set the right initial value 
    
for el1 in extLightsList:
    extData[el1]=0 # change'0' with signal.initial to set the right initial value

for e1 in engine1list:
    engineData[e1]=0 # change'0' with signal.initial to set the right initial value

for e1 in brakelist:
    brakeData[e1]=0 # change'0' with signal.initial to set the right initial value

# Set the desired values for ignition + engine on + Powertrain (KEY ON), right turning arrows
ignData['CmdIgnSts'] = 4
extData['RHTurnSignalSts'] = 1
engineData['EngineSts'] = 2
engineData['PowertrainPrplsnActv'] = 1
brakeData['VehicleSpeedVSOSig'] = 0

# Encoding the messages 
data_BCM_COMMAND = BCM_COMMAND.encode(ignData)
data_ENGINE1 = ENGINE1.encode(engineData)
data_EXT_LIGHTS = EXT_LIGHTS.encode(extData)
data_BRAKE1 = BRAKE1.encode(brakeData)

# Create the message to be sent: pass the ID, the lenght, the payload and KEEP ATTENTION to the extended id(
# che for the 'x' at the end of the ID in the db)
msgign=can.Message(arbitration_id=250, dlc=BCM_COMMAND.length, data=data_BCM_COMMAND, is_extended_id=False) # BCM_COMMAND.frame_id
msgext=can.Message(arbitration_id=EXT_LIGHTS.frame_id, dlc=EXT_LIGHTS.length, data=data_EXT_LIGHTS, is_extended_id=False)
msgeng=can.Message(arbitration_id=ENGINE1.frame_id, dlc=ENGINE1.length, data=data_ENGINE1, is_extended_id=False)
msgbra=can.Message(arbitration_id=BRAKE1.frame_id, dlc=BRAKE1.length, data=data_BRAKE1, is_extended_id=False)

# Send messages
try:
    can_c1.send_periodic(msgign,0.01) # Send a periodic message into the CAN network with a periodicity of 10 ms
    can_c1.send_periodic(msgeng,0.01) # Send a periodic message into the CAN network with a periodicity of 10 ms
    print("message sent on {}".format(can_c1.channel_info)) 
except can.CanError:
    print("message not sent")


can_bh.send_periodic(msgext,0.250) # Send a periodic message into the CAN network with a periodicity of 250 ms

brakeData['VehicleSpeedVSOSig'] = 0
data_BRAKE1 = BRAKE1.encode(brakeData)
msgbra=can.Message(arbitration_id=BRAKE1.frame_id, dlc=BRAKE1.length, data=data_BRAKE1, is_extended_id=False)
can_c1.send_periodic(msgbra,0.01)
print("Sent speed 0")

time.sleep(5) # Wait for 5 s

# Take a picture of the cluster 
result, image = cam.read()
results = reader.readtext(image, detail = 0, paragraph = True)
print(results)

'''
# Set the speed to 30 
brakeData['VehicleSpeedVSOSig'] = 30
data_BRAKE1 = BRAKE1.encode(brakeData)
msgbra=can.Message(arbitration_id=BRAKE1.frame_id, dlc=BRAKE1.length, data=data_BRAKE1, is_extended_id=False)
can_c1.send_periodic(msgbra,0.01)
print("Sent speed 30")
time.sleep(5)
result, image = cam.read()

image2 = image[230:300,250:400] 
results = reader.readtext(image2, detail = 0, paragraph = True)
print(results)


# Set the speed to 70
brakeData['VehicleSpeedVSOSig'] = 70
data_BRAKE1 = BRAKE1.encode(brakeData)
msgbra=can.Message(arbitration_id=BRAKE1.frame_id, dlc=BRAKE1.length, data=data_BRAKE1, is_extended_id=False)
can_c1.send_periodic(msgbra,0.01)
print("Sent speed 70")
time.sleep(5)
result, image = cam.read()

image2 = image[230:300,250:400] 
results = reader.readtext(image2, detail = 0, paragraph = True)
print(results)




'''
'''


while True:
    
    message = can_c1.recv() # Read a message from the CAN network C1: Timestamp, signals values, ID etc.
    message2 = can_bh.recv() # Read a message from the CAN network BH: Timestamp, signals values, ID etc.

    #if(message.arbitration_id == BCM_COMMAND.frame_id): 
    #print(db.decode_message(message.arbitration_id, message.data))
    #print(message)
    #if(message2.arbitration_id == EXT_LIGHTS.frame_id): 
    #    print(dbb.decode_message(message2.arbitration_id, message2.data))  
    #print(dbb.decode_message(message2.arbitration_id, message2.data))
    


#can_c1.send_periodic(msgign,0.01)
    #can_c1.send(msgign)
    #can_bh.send(msgext)



can_c1.shutdown()
can_bh.shutdown()



'''
#data_BRAKE1= BRAKE1.encode({'EngineSts': 2})