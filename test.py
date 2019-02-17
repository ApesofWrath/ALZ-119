import cscore as cs

from networktables import NetworkTables

def startNetworkTables():

    NetworkTables.startClientTeam(668)
    NetworkTables.initialize(server='10.6.68.2') #roborio must be on this static ip
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    print("Connected!")


startNetworkTables()
table = NetworkTables.getTable('SmartDashboard')


server = cs.CameraServer(





