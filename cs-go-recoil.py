import pymem
from time import sleep
import requests

def get_offset(url = "https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the JSON file: {e}")
        return None

def recoil(offsets = get_offset()) -> None:
    pm = pymem.Pymem('csgo.exe') # find csgo.exe
    
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll # access client.dll
    engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll # access engine.dll
    
    oldPunch = (0.0, 0.0)

    while True:
        sleep(.01)

        localPlayer = pm.read_uint(client + offsets["signatures"]["dwLocalPlayer"])
        shotsFired = pm.read_int(localPlayer + offsets["netvars"]["m_iShotsFired"])

        if shotsFired: 

            clientState = pm.read_uint(engine + offsets["signatures"]["dwClientState"])
            viewAnglesX = pm.read_float(clientState + offsets["signatures"]["dwClientState_ViewAngles"])
            viewAnglesY = pm.read_float(clientState + offsets["signatures"]["dwClientState_ViewAngles"] + 4)

            aimPunchX = pm.read_float(localPlayer + offsets["netvars"]["m_aimPunchAngle"])
            aimPunchY = pm.read_float(localPlayer + offsets["netvars"]["m_aimPunchAngle"] + 4)

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

            pm.write_float(clientState + offsets["signatures"]["dwClientState_ViewAngles"], newAngles[0])
            pm.write_float(clientState + offsets["signatures"]["dwClientState_ViewAngles"] + 4, newAngles[1])
            
            oldPunch = (aimPunchX * 2.0, aimPunchY * 2.0)
        else:
            oldPunch = (0.0, 0.0)

if __name__ == "__main__":
    recoil()