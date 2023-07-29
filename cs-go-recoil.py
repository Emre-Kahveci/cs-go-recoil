import pymem
from time import sleep

offsets = {
    "localPlayer": 0xDEA98C,
    "clientState": 0x59F19C,
    "clientState_ViewAngles": 0x4D90,
    'aimPunchAngle': 0x303C,
    'shotsFired': 0x103E0
}

def recoil() -> None:
    pm = pymem.Pymem('csgo.exe') # find csgo.exe
    
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll # access client.dll
    engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll # access engine.dll
    
    oldPunch = (0.0, 0.0)

    while True:
        sleep(.01)

        localPlayer = pm.read_uint(client + offsets["localPlayer"])
        shotsFired = pm.read_int(localPlayer + offsets["shotsFired"])

        if shotsFired: 

            clientState = pm.read_uint(engine + offsets["clientState"])
            viewAnglesX = pm.read_float(clientState + offsets["clientState_ViewAngles"])
            viewAnglesY = pm.read_float(clientState + offsets["clientState_ViewAngles"] + 4)

            aimPunchX = pm.read_float(localPlayer + offsets["aimPunchAngle"])
            aimPunchY = pm.read_float(localPlayer + offsets["aimPunchAngle"] + 4)

            newAngles = (
                viewAnglesX + oldPunch[0] - aimPunchX * 2.0,
                viewAnglesY + oldPunch[1] - aimPunchY * 2.0
            )
        
            if (newAngles[0] > 89.0):
                newAngles = (
                    89.0,
                    viewAnglesY + oldPunch[1] - aimPunchY * 2.0
                )

            if (newAngles[0] < -89.0):
                newAngles = (
                    -89.0,
                    viewAnglesY + oldPunch[1] - aimPunchY * 2.0
                )
            
            while (newAngles[1] > 360.0):
                newAngles = (
                    viewAnglesX + oldPunch[0] - aimPunchX * 2.0,
                    newAngles[1] - 360.0
                    )
                
            while (newAngles[1] < -360.0):
                newAngles = (
                    viewAnglesX + oldPunch[0] - aimPunchX * 2.0,
                    newAngles[1] + 360.0
                    )

            pm.write_float(clientState + offsets["clientState_ViewAngles"], newAngles[0])
            pm.write_float(clientState + offsets["clientState_ViewAngles"] + 4, newAngles[1])
            
            oldPunch = (aimPunchX * 2.0, aimPunchY * 2.0)
        else:
            oldPunch = (0.0, 0.0)

if __name__ == "__main__":
    recoil()