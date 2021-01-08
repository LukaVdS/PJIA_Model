# PJIA_Model

## Run PJIA_server.py to run on the server. 
To change parameters, open parameters.py

Aircraft (black filled circles) come in according to a schedule, they carry cargo (small orange squares). Aircraft moves over taxi ways to a free parking spot and wait.

A coordinator (red dot) sees the parked aircraft and goes to check amount and type of cargo. Coordinator has a maximum memory capacity, in this case max 2 aircraft can be checked, before the information is passed to offloader. When ‘memory’ is full, the coordinator goes to the offloader building to give the information about the aircraft.

The offloader (green dot) goes to a vehicle (blue square) to go offload the aircraft. After cargo is offloaded, aircraft can exit and cargo is brought to cargo/terminal building. When there are no aircraft to be checked, the vehicle is parked and the offloader goes back to its building.

The simulation stops running 50 steps after the last aircraft has exited.

Furhtermore:
    Aircraft get checked and offloaded according to the longest waiting on the parking spot.
    Next version will include an offloading coordinator and multiple offloaders, vehicles and cargo types.
    
