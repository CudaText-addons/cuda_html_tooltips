import re
import json
from cudatext import *
from .colorcodes import *


MY_TAG = 101 #uniq value for all plugins with ed.hotspots()
REGEX_COLORS = r'(\#[0-9a-f]{3}\b)|(\#[0-9a-f]{6}\b)'
re_compiled = re.compile(REGEX_COLORS, re.I)
FORM_W = 200
FORM_H = 60
HINT_PADDING = 6


class Command:
    def __init__(self):

        self.init_form()

    def on_change_slow(self, ed_self):

        self.find_colors()

    def on_open(self, ed_self):

        self.find_colors()

    def find_colors(self):

        ed.hotspots(HOTSPOT_DELETE_BY_TAG, tag=MY_TAG)
        count = 0

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
                count += 1
        #print('HTML Tooltips: %d items'%count)


    def on_hotspot(self, ed_self, entered, hotspot_index):

        if entered:
            hotspot = ed.hotspots(HOTSPOT_GET_LIST)[hotspot_index]

            data = json.loads(hotspot['tag_str'])
            color = HTMLColorToPILColor(data['s'])
            pos_x = data['x']
            pos_y = data['y']

            pos = ed.convert(CONVERT_CARET_TO_PIXELS, x=pos_x, y=pos_y)

            cell_size = ed.get_prop(PROP_CELL_SIZE)
            ed_coord = ed.get_prop(PROP_COORDS)
            ed_size_x = ed_coord[2]-ed_coord[0]
            ed_size_y = ed_coord[3]-ed_coord[1]
            hint_x = pos[0]
            hint_y = pos[1] + cell_size[1] + HINT_PADDING
            #no space for tooltip on bottom?
            if hint_y + FORM_H > ed_size_y:
                hint_y = pos[1] - FORM_H - HINT_PADDING

            dlg_proc(self.h_dlg, DLG_PROP_SET, prop={
                    'p': ed_self.h,
                    'x': hint_x,
                    'y': hint_y,
                    'color': color,
                    })
            dlg_proc(self.h_dlg, DLG_SHOW_NONMODAL)

        else:
            dlg_proc(self.h_dlg, DLG_HIDE)


    def init_form(self):

        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg = h

        dlg_proc(h, DLG_PROP_SET, prop={
                'w': FORM_W,
                'h': FORM_H,
                'border': False
                })
