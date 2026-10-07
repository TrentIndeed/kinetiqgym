"""Picture for R3-5: the Pi and BMS hang upside down from bosses in the cover ceilings. Renders the two covers with the Pi and the BMS,
seen from below (looking up), to ceiling-mounts.png."""
from pathlib import Path
import os, subprocess
import cadquery as cq

H = Path(__file__).resolve().parent
parts = {'V44_PRINT_cover_left_screen': (0.55, 0.57, 0.6), 'V44_PRINT_cover_right_grille': (0.55, 0.57, 0.6),
         'TRIAL_Pi4_upright': (0.1, 0.55, 0.25), 'JBD_SP17S005_BMS_mock_from_spec': (0.1, 0.35, 0.75),
         'MOUNT_Pi_ceiling_standoffs_M2.5': (0.8, 0.7, 0.3), 'MOUNT_BMS_ceiling_standoffs_M3': (0.8, 0.7, 0.3)}
comp = cq.Compound.makeCompound([cq.Shape.importBrep(str(H / 'printed' / (n + '.brep'))) for n in parts])
svg = H / 'ceiling-mounts.svg'
cq.exporters.export(cq.Workplane().add(comp), str(svg), opt=dict(projectionDir=(0.15, 0.25, -1.0), width=1400, height=700, showHidden=False, strokeWidth=0.35))
edge = os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), r'Microsoft\Edge\Application\msedge.exe')
subprocess.run([edge, '--headless=new', '--disable-gpu', f'--screenshot={H / "ceiling-mounts.png"}', '--window-size=1420,720', 'file:///' + str(svg).replace('\\', '/')], capture_output=True, timeout=120)
print('ok')
