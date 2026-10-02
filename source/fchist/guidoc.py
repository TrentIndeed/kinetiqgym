"""Write a FreeCAD GuiDocument.xml (visibility + colour per object) into an .FCStd made without the GUI."""
import re, struct, zipfile, os

def _packed(r, g, b, a=1.0):
    return (int(round(r * 255)) << 24) | (int(round(g * 255)) << 16) | (int(round(b * 255)) << 8) | int(round(a * 255))

def appearance(rgb, transparency=0.0):
    """PropertyMaterialList file, version 3: one material."""
    r, g, b = rgb
    return (struct.pack('<I', 1) + struct.pack('<IIII', _packed(.333, .333, .333), _packed(r, g, b), _packed(.533, .533, .533), _packed(0, 0, 0))
            + struct.pack('<ff', 0.9, transparency) + struct.pack('<III', 0, 0, 0))

CAM = ('OrthographicCamera {&#10;  viewportMapping ADJUST_CAMERA&#10;  position 600 -900 700&#10;  orientation 0.8 0.3 0.4  1.2&#10;'
       '  nearDistance 1&#10;  farDistance 5000&#10;  aspectRatio 1&#10;  focalDistance 1200&#10;  height 600&#10;&#10;}&#10;')

def write(fcstd, style):
    """style: {object name: (visible, (r, g, b) or None)}; objects not listed are hidden."""
    z = zipfile.ZipFile(fcstd)
    names = [n for n in z.namelist() if n != 'GuiDocument.xml' and not n.startswith('fchApp')]
    objs = re.findall(r'<Object type="[^"]+" name="([^"]+)"', z.read('Document.xml').decode('utf-8'))
    vps, files = [], {}
    for k, n in enumerate(objs):
        vis, col = style.get(n, (False, None))
        props = ['<Property name="Visibility" type="App::PropertyBool" status="1">\n<Bool value="%s"/>\n</Property>' % ('true' if vis else 'false')]
        if col is not None:
            fn = 'fchApp%d' % k; files[fn] = appearance(col)
            props.append('<Property name="ShapeAppearance" type="App::PropertyMaterialList" status="1">\n<MaterialList file="%s" version="3"/>\n</Property>' % fn)
        vps.append('<ViewProvider name="%s" expanded="0">\n<Properties Count="%d" TransientCount="0">\n%s\n</Properties>\n</ViewProvider>'
                   % (n, len(props), '\n'.join(props)))
    gui = ("<?xml version='1.0' encoding='utf-8'?>\n<!--\n FreeCAD Document, see https://www.freecad.org for more information...\n-->\n"
           '<Document SchemaVersion="1" HasExpansion="1">\n<Expand />\n'
           '<ViewProviderData Count="%d">\n%s\n</ViewProviderData>\n<Camera settings="%s"/>\n</Document>\n' % (len(vps), '\n'.join(vps), CAM))
    tmp = fcstd + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as w:
        for n in names: w.writestr(n, z.read(n))
        w.writestr('GuiDocument.xml', gui)
        for fn, b in files.items(): w.writestr(fn, b)
    z.close(); os.replace(tmp, fcstd)
