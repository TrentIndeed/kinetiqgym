"""Round 5 picture: the handle loop at the motor end, seen from behind and the motor end (thin side faces the rear), with the
CAN board standing on its standoffs behind the motor. Writes handle-round5.png."""
from pathlib import Path
import os, subprocess
import cadquery as cq

H = Path(__file__).resolve().parent
names = ['S01_V44_PRINT_bottom_plate_left', 'V44_PRINT_end_cap_motor', 'V44_PRINT_cover_left_screen']
comp = cq.Compound.makeCompound([cq.Shape.importBrep(str(H / 'printed' / (n + '.brep'))) for n in names])
svg = H / 'handle-round5.svg'
cq.exporters.export(cq.Workplane().add(comp), str(svg), opt=dict(projectionDir=(-0.8, 1.0, -0.45), width=1200, height=800, showHidden=False, strokeWidth=0.35))
edge = os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), r'Microsoft\Edge\Application\msedge.exe')
subprocess.run([edge, '--headless=new', '--disable-gpu', f'--screenshot={H / "handle-round5.png"}', '--window-size=1220,820', 'file:///' + svg.as_posix()], capture_output=True, timeout=120)
svg.unlink()
print('ok')
