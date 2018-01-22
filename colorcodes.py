### http://code.activestate.com/recipes/266466-html-colors-tofrom-rgb-tuples/
import colorsys

def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '#%02x%02x%02x' % rgb_tuple
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor

def HTMLColorToRGB(s):
    """ convert #RRGGBB to an (R, G, B) tuple """
    s = s.strip()
    if s[0] == '#': s = s[1:]
    if len(s)==3:
        s = s[0]*2 + s[1]*2 + s[2]*2
    if len(s) != 6:
        raise ValueError("input #%s is not in #RRGGBB format" % s)
    r, g, b = s[:2], s[2:4], s[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)

def HTMLColorToPILColor(s):
    """ converts #RRGGBB or #RGB to integers"""
    s = s.strip()
    while s[0] == '#': s = s[1:]
    # get bytes in reverse order to deal with PIL quirk
    if len(s)==3:
        s = s[0]*2 + s[1]*2 + s[2]*2
    if len(s)!=6:
        raise Exception('Incorrect color token: '+s)
    s = s[-2:] + s[2:4] + s[:2]
    # finally, make it numeric
    color = int(s, 16)
    return color

def PILColorToRGB(pil_color):
    """ convert a PIL-compatible integer into an (r, g, b) tuple """
    hexstr = '%06x' % pil_color
    # reverse byte order
    r, g, b = hexstr[4:], hexstr[2:4], hexstr[:2]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)

def PILColorToHTMLColor(pil_integer):
    return RGBToHTMLColor(PILColorToRGB(pil_integer))

def RGBToPILColor(rgb_tuple):
    return HTMLColorToPILColor(RGBToHTMLColor(rgb_tuple))


def RGBToHLS(r, g, b):
    return colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)

def float_to_percent(x):
    return '%.0f'%(x*100)+'%'

def float_to_degrees(x):
    return str(round(x*360))+'°'
