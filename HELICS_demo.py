import helics
import logging
import sys
import socket

""""
Runner file for the HELICS+ Large Scale Demo
Each node will run this script and determine if they are the main node or a sub node

input params: main node id, house_fed_start, house_fed_end
Creates central controller federate if on main node
Creates callback federates

"""

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

class UserData(object):
    def __init__(self,name, gridlabd_ept, centralcontroller_ept):
        self.name = name
        self.gridlabd_ept = gridlabd_ept
        self.centralcontroller_ept = centralcontroller_ept

@helics.ffi.callback("void (HelicsTime newTime, int iterating, void *user_data)")

def Callback(time, iterating, userData):
    new_temp = userdata.centralcontroller_ept.get_message()
    house_name=userdata.name
    logger.info(f"msg received: {new_temp}")
    msg = f" \"{{\"{house_name}\":{{\"cooling_setpoint\":{new_temp}}}}}\""
    userdata.gridlabd_ept.send_data(msg)

def destroyfederate(fed):
    helics.helicsFederateDisconnect(fed)
    helics.helicsFederateFree(fed)
    helics.helicsCloseLibrary()

def createFedInfo(name, broker_name, broker_address):
    fed_init_string = f"--broker={broker_name} --broker_address={broker_address} --federates=1"
    fed_info = helics.helicsCreateFederateInfo()
    helics.helicsFederateInfoSetCoreTypeFromString(fed_info, "zmqss")
    helics.helicsFederateInfoSetCoreName(fed_info, f'{name}_core')          
    helics.helicsFederateInfoSetCoreInitString(fed_info, fed_init_string)
    return fed_info

def createCallbackFederate(name, broker_name, broker_address):
    fed_info = createFedInfo(name, broker_name, broker_address)
    fed = helics.helicsCreateCallbackFederate(name, fed_info)   
    helics.helicsFederateSetFlagOption(fed, helics.HELICS_FLAG_EVENT_TRIGGERED, 1)
    return fed


if __name__=="__main__":                                         
    main_node_id = sys.argv[1]                                  
    start_fed_num = int(sys.argv[2])                                   
    end_fed_num = int(sys.argv[3])
    self_node_id = socket.gethostname()
    gridlabd_instance = socket.gethostname()             
    root_broker_address = "tcp://"+str(socket.gethostbyname(main_node_id))      
    self_address = "tcp://"+str(socket.gethostbyname(self_node_id))

    num_houses = end_fed_num - start_fed_num + 1
    gridlabd_instance_name = "gridlabd_" + gridlabd_instance


    if main_node_id == self_node_id:
        num_feds = num_houses + 2                                         #add gridlabd fed & central controller
        logger.info(f"Creating central controller federate @ {self_address} = {root_broker_address}")
        fedinfo = helics.helicsCreateFederateInfo()
        fedinfo.core_name = "centralcontroller"
        fedinfo.core_type = "zmqss"
        fedinfo.core_init = f"-f 1 --broker=mainbroker --broker_address={self_address}"
        central_controller_fed = helics.helicsCreateCombinationFederate("centralcontroller", fedinfo)
        helics.helicsFederateRegisterEndpoint(central_controller_fed, "centralcontroller")
        central_controller_sub = helics.helicsFederateRegisterSubscription(central_controller_fed, "centralcontroller/gridlabd", "VA")
        broker_name = "mainbroker"
        
    else:
        num_feds=num_houses+1                                             
        broker_name = f'subbroker_{self_node_id}'

    
    house_feds=[]

    
    # create house federates, register targeted endpts
    logger.info("Creating callback federates connecting to broker at " + self_address)
    for num in range(start_fed_num, end_fed_num+1):
        house_name=f"house_${num}"  
        fed=createCallbackFederate(house_name, broker_name, self_address)
        house_feds.append(fed)

        # register a targeted endpoint to gridlabd_instance federate
        house_gridlabd_endpt=helics.helicsFederateRegisterTargetedEndpoint(fed, f'{house_name}/{gridlabd_instance_name}')
        helics.helicsEndpointAddDestinationTarget(house_gridlabd_endpt, gridlabd_instance_name)

        # register a targeted endpoint to central controller federate
        house_central_controller_endpt = helics.helicsFederateRegisterTargetedEndpoint(fed, f'{house_name}/{"centralcontroller"}')
        helics.helicsEndpointAddSourceTarget(house_central_controller_endpt, "centralcontroller")

        # set time return callback
        # time request triggered by event 
        # callback will receive message from central contorller & send message to gridlabd federate
        userdata=UserData(house_name, house_gridlabd_endpt, house_central_controller_endpt)
        handle = helics.ffi.new_handle(userdata)
        helics.helicsFederateSetTimeRequestReturnCallback(fed, Callback, handle)

    ##### Enter Initialization Mode #####
    logger.info(f"ENTERING INITIALIZATION MODE {self_node_id}")
    for fed in house_feds:
        helics.helicsFederateEnterInitializingMode(fed)


    ##### Enter Execution Mode #####
    logger.info(f"ENTERING EXECUTION MODE {self_node_id}")

    if main_node_id == self_node_id:
        helics.helicsFederateEnterExecutingModeAsync(central_controller_fed)
        helics.helicsFederateEnterExecutingModeComplete(central_controller_fed)
    logger.info("hang check")

    hours = 8
    total_interval = int(60*60*hours)
    time_step = 15*60
    time_granted = -1
    threshold = 100
    init_values = True

    
    if main_node_id == self_node_id:
        while time_granted <= total_interval:
            logger.info("time enter")
            time_granted = helics.helicsFederateRequestTime(central_controller_fed, time_step)
            value = central_controller_fed.subscriptions[f"centralcontroller/gridlabd"].value
            logger.info(f"CENTRAL CONTROLLER: Received value = {value} at time {time_granted}")

            if value == threshold:
                new_value = value
            elif value < threshold:
                new_value = value+1
            else:
                new_value = value-1

            helics.helicsEndpointSendMessage(central_controller_fed.get_endpoint_by_name("centralcontroller"), new_value)
            print("new temp:" + new_value)

    ##### cleanup #####
    for fed in house_feds:
        destroyfederate(fed)
    if main_node_id == self_node_id: destroyfederate(central_controller_fed)

        


 