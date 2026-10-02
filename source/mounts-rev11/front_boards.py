"""V44 fix list round 6: the Teensy, CAN board and regulator stand on one printed plate at the front-left corner (left of the
screen, in front of the motor), components facing the motor. Shared by make_design_layout.py (board assemblies) and
build_mounts.py (their standoffs, the plate and the lead spaces), so the boards and their standoffs move together.

Each board is turned about its own box centre and put so that its standoff far ends (the old rear-plate face, Y 2.5) land on
the plate face (Y -129.5). World frame: X along the shaft (motor at -X), -Y front, Z up, base plate top Z 0."""
import numpy as np
from scipy.spatial.transform import Rotation as Rot

PLATE = dict(x=(-77.0, -38.5), y=(-133.5, -129.5), z=(0.5, 78.0), foot_y=(-129.5, -125.5), foot_z=(0.5, 5.0))
PLATE_SCREWS = [(-70.0, -127.5), (-46.0, -127.5)]          # M3 up through the bottom plate into foot inserts
OLD_FACE_Y = 2.5                                           # round 5 standoff far ends (rear plate face)

# Board box centres after round 5 (rev 12 world): board piece boxes from the page.
NOW = {'teensy': np.array([(-51.98 - 12.42) / 2, (-16.8 - 5.2) / 2, (48.01 + 69.79) / 2]),
       'TRIAL_CAN_headers': np.array([(-74.0451 - 37.5549) / 2, (-21.8892 - 3.5108) / 2, (3.9622 + 18.2378) / 2]),
       'regulator': np.array([(-4.0 + 25.4) / 2, (-20.0124 - 4.5876) / 2, (28.0 + 57.4) / 2])}
RZ = Rot.from_rotvec([0, 0, np.pi])                        # components turn from facing the front to facing the motor
ROT = {'teensy': Rot.from_rotvec([0, np.pi / 2, 0]) * RZ,             # long axis vertical, USB end (+X) on top
       'TRIAL_CAN_headers': Rot.from_rotvec([0, -np.pi / 2, 0]) * RZ,  # long axis vertical, screw terminal (-X end) on top
       'regulator': RZ}
# Target board box centres in X and Z on the plate: regulator low across the plate, Teensy (left) and CAN board (right) above it.
TARGET_XZ = {'teensy': (-66.1, 57.8), 'TRIAL_CAN_headers': (-46.1, 56.2), 'regulator': (-62.3, 20.7)}

def target(a):
    x, z = TARGET_XZ[a]
    return np.array([x, PLATE['y'][1] + (OLD_FACE_Y - NOW[a][1]), z])

def world(a, p):
    """Round 5 world point of board assembly `a` -> its round 6 world point."""
    return ROT[a].apply(np.asarray(p, float) - NOW[a]) + target(a)
