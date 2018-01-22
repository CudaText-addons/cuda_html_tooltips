import re
import json
from cudatext import *
from .colorcodes import *


MY_TAG = 101 #uniq value for all plugins with ed.hotspots()
REGEX_COLORS = r'(\#[0-9a-f]{3}\b)|(\#[0-9a-f]{6}\b)'
re_compiled = re.compile(REGEX_COLORS, re.I)


class Command:
    def __init__(self):

        self.init_form()


    def find_colors(self):

        ed.hotspots(HOTSPOT_DELETE_BY_TAG, tag=MY_TAG)
        for nline in range(ed.get_line_count()):
            line = ed.get_text_line(nline)
            items = re_compiled.finditer(line)
            for item in items:
                span = item.span()
                substr = line[span[0]:span[1]]
                data = json.dumps({
                        's': substr,
                        'x': span[0],
                        'x2': span[1],
                        'y': nline
                        })

                ed.hotspots(HOTSPOT_ADD,
                            tag=MY_TAG,
                            tag_str=data,
                            pos=(span[0], nline, span[1], nline)
                            )


    def on_hotspot(self, ed_self, entered, hotspot_index):

        if entered:
            hotspot = ed.hotspots(HOTSPOT_GET_LIST)[hotspot_index]

            data = json.loads(hotspot['tag_str'])
            color = HTMLColorToPILColor(data['s'])
            pos_x = data['x']
            pos_y = data['y']

            pos = ed.convert(CONVERT_CARET_TO_PIXELS, x=pos_x, y=pos_y)

            dlg_proc(self.h_dlg, DLG_PROP_SET, prop={
                    'x':pos[0],
                    'y':pos[1]+25,
                    'color':color,
                    'p':ed_self.h
                    })
            dlg_proc(self.h_dlg, DLG_SHOW_NONMODAL)

        else:
            dlg_proc(self.h_dlg, DLG_HIDE)


    def init_form(self):

        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg = h

        dlg_proc(h, DLG_PROP_SET, prop={'w':300, 'h':50, 'border':False})
