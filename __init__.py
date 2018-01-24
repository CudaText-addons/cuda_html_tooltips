import re
import json
import os
from cudatext import *
from .colorcodes import *
from html.parser import HTMLParser

MY_TAG = 101 #uniq value for all plugins with ed.hotspots()

REGEX_COLORS = r'(\#[0-9a-f]{3}\b)|(\#[0-9a-f]{6}\b)'
REGEX_RGB = r'\brgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,\s*\d+\s*)?\)'
REGEX_PIC = r'(\'|")[^\'"]+?\.(png|gif|jpg|jpeg|bmp|ico)\1'
REGEX_PIC_CSS = r'\([^\'"\(\)]+?\.(png|gif|jpg|jpeg|bmp|ico)\)'
REGEX_ENT = r'&\w+;'

html_parser = HTMLParser()
re_colors_compiled = re.compile(REGEX_COLORS, re.I)
re_rgb_compiled = re.compile(REGEX_RGB, re.I)
re_pic_compiled = re.compile(REGEX_PIC, re.I)
re_pic_css_compiled = re.compile(REGEX_PIC_CSS, re.I)
re_ent_compiled = re.compile(REGEX_ENT, 0)

FORM_COLOR_W = 170
FORM_COLOR_H = 100
FORM_PIC_W = 300
FORM_PIC_H = 240
FORM_ENT_W = 50
FORM_ENT_H = 50
FORM_ENT_FONT_SIZE = 28
FORM_GAP = 4
FORM_GAP_OUT = 8
COLOR_FORM_BACK = 0x505050
COLOR_FORM_FONT = 0xE0E0E0
COLOR_FORM_FONT2 = 0x40E0E0
COLOR_FORM_PANEL_BORDER = 0xFFFFFF


class Command:
    def __init__(self):

        self.init_form_color()
        self.init_form_pic()
        self.init_form_ent()

    def on_change_slow(self, ed_self):

        self.find_hotspots()

    def on_open(self, ed_self):

        self.find_hotspots()

    def find_hotspots(self):

        ed.hotspots(HOTSPOT_DELETE_BY_TAG, tag=MY_TAG)
        count = 0

        for nline in range(ed.get_line_count()):
            line = ed.get_text_line(nline)

            #find entities
            for item in re_ent_compiled.finditer(line):
                span = item.span()
                data = json.dumps({
                        'ent': item.group(0),
                        'x': span[0],
                        'y': nline,
                        })

                ed.hotspots(HOTSPOT_ADD,
                            tag=MY_TAG,
                            tag_str=data,
                            pos=(span[0], nline, span[1], nline)
                            )
                count += 1

            #find colors
            for item in re_colors_compiled.finditer(line):
                span = item.span()
                data = json.dumps({
                        'color': item.group(0),
                        'x': span[0],
                        'y': nline,
                        })

                ed.hotspots(HOTSPOT_ADD,
                            tag=MY_TAG,
                            tag_str=data,
                            pos=(span[0], nline, span[1], nline)
                            )
                count += 1

            #find rgb
            for item in re_rgb_compiled.finditer(line):
                span = item.span()
                data = json.dumps({
                        'rgb': item.group(0),
                        'r': int(item.group(1)),
                        'g': int(item.group(2)),
                        'b': int(item.group(3)),
                        'x': span[0],
                        'y': nline,
                        })

                ed.hotspots(HOTSPOT_ADD,
                            tag=MY_TAG,
                            tag_str=data,
                            pos=(span[0], nline, span[1], nline)
                            )
                count += 1

            #find pics, only for named files
            if ed.get_filename():
                for item in re_pic_compiled.finditer(line):
                    span = item.span()
                    text = item.group(0)[1:-1]
                    if 'http://' in text: continue
                    if 'https://' in text: continue

                    data = json.dumps({
                            'pic': text,
                            'x': span[0],
                            'y': nline,
                            })

                    ed.hotspots(HOTSPOT_ADD,
                                tag=MY_TAG,
                                tag_str=data,
                                pos=(span[0], nline, span[1], nline)
                                )
                    count += 1

            #same for CSS pics
            if ed.get_filename() and ('CSS' in ed.get_prop(PROP_LEXER_FILE)):
                for item in re_pic_css_compiled.finditer(line):
                    span = item.span()
                    text = item.group(0)[1:-1]
                    if 'http://' in text: continue
                    if 'https://' in text: continue

                    data = json.dumps({
                            'pic': text,
                            'x': span[0],
                            'y': nline,
                            })

                    ed.hotspots(HOTSPOT_ADD,
                                tag=MY_TAG,
                                tag_str=data,
                                pos=(span[0], nline, span[1], nline)
                                )
                    count += 1

            #print('HTML Tooltips: %d items'%count)


    def on_hotspot(self, ed_self, entered, hotspot_index):

        if not entered:
            self.hide_forms()
        else:
            hotspot = ed.hotspots(HOTSPOT_GET_LIST)[hotspot_index]
            if hotspot['tag'] != MY_TAG: return

            data = json.loads(hotspot['tag_str'])
            text = data.get('color', '')
            if text:
                self.update_form_color(text)
                h_dlg = self.h_dlg_color
            else:
                text = data.get('pic', '')
                if text:
                    if not self.update_form_pic(text): return
                    h_dlg = self.h_dlg_pic
                else:
                    text = data.get('ent', '')
                    if text:
                        if not self.update_form_ent(text): return
                        h_dlg = self.h_dlg_ent
                    else:
                        text = data.get('rgb', '')
                        if text:
                            self.update_form_rgb(text, data['r'], data['g'], data['b'])
                            h_dlg = self.h_dlg_color
                        else:
                            return

            prop = dlg_proc(h_dlg, DLG_PROP_GET)
            form_w = prop['w']
            form_h = prop['h']

            pos_x = data['x']
            pos_y = data['y']
            pos = ed.convert(CONVERT_CARET_TO_PIXELS, x=pos_x, y=pos_y)

            cell_size = ed.get_prop(PROP_CELL_SIZE)
            ed_coord = ed.get_prop(PROP_COORDS)
            ed_size_x = ed_coord[2]-ed_coord[0]
            ed_size_y = ed_coord[3]-ed_coord[1]
            hint_x = pos[0]
            hint_y = pos[1] + cell_size[1] + FORM_GAP_OUT

            #no space on bottom?
            if hint_y + form_h > ed_size_y:
                hint_y = pos[1] - form_h - FORM_GAP_OUT

            #no space on right?
            if hint_x + form_w > ed_size_x:
                hint_x = ed_size_x - form_w

            dlg_proc(h_dlg, DLG_PROP_SET, prop={
                    'p': ed_self.h, #set parent to Editor handle
                    'x': hint_x,
                    'y': hint_y,
                    })
            dlg_proc(h_dlg, DLG_SHOW_NONMODAL)


    def hide_forms(self):

        dlg_proc(self.h_dlg_color, DLG_HIDE)
        dlg_proc(self.h_dlg_pic, DLG_HIDE)
        dlg_proc(self.h_dlg_ent, DLG_HIDE)


    def init_form_color(self):

        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg_color = h

        dlg_proc(h, DLG_PROP_SET, prop={
                'w': FORM_COLOR_W,
                'h': FORM_COLOR_H,
                'border': False,
                'color': COLOR_FORM_BACK,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'colorpanel')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'panel_color',
                'x': FORM_GAP,
                'y': FORM_GAP,
                'w': FORM_COLOR_W-2*FORM_GAP,
                'h': 26,
                'props': (1,0x808080,0x202020,COLOR_FORM_PANEL_BORDER),
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_text',
                'cap': '??',
                'font_color': COLOR_FORM_FONT2,
                'x': FORM_GAP,
                'y': 26+2*FORM_GAP,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_rgb',
                'cap': '??',
                'font_color': COLOR_FORM_FONT,
                'x': FORM_GAP,
                'y': 46+2*FORM_GAP,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_hls',
                'cap': '??',
                'font_color': COLOR_FORM_FONT,
                'x': FORM_GAP,
                'y': 66+2*FORM_GAP,
                })


    def init_form_pic(self):

        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg_pic = h

        dlg_proc(h, DLG_PROP_SET, prop={
                'w': FORM_PIC_W,
                'h': FORM_PIC_H,
                'border': False,
                'color': COLOR_FORM_BACK,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_text',
                'cap': '??',
                'font_color': COLOR_FORM_FONT,
                'x': FORM_GAP,
                'y': FORM_GAP,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'image')
        self.h_img = dlg_proc(h, DLG_CTL_HANDLE, index=n)
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'img',
                'x': FORM_GAP,
                'y': 20+2*FORM_GAP,
                'w': FORM_PIC_W-2*FORM_GAP,
                'h': FORM_PIC_H-20-3*FORM_GAP,
                'props': (
                    True, #center
                    True, #stretch
                    True, #stretch in
                    False, #stretch out
                    True, #keep origin x
                    True, #keep origin y
                    )
                })


    def init_form_ent(self):

        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg_ent = h

        dlg_proc(h, DLG_PROP_SET, prop={
                'w': FORM_ENT_W,
                'h': FORM_ENT_H,
                'border': False,
                'color': COLOR_FORM_BACK,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'colorpanel')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_text',
                'cap': '??',
                'color': COLOR_FORM_BACK,
                'font_color': COLOR_FORM_FONT,
                'font_size': FORM_ENT_FONT_SIZE,
                'align': ALIGN_CLIENT,
                })


    def update_form_color(self, text):

        ncolor = HTMLColorToPILColor(text)
        r, g, b = HTMLColorToRGB(text)
        self.update_form_color_ex(text, ncolor, r, g, b)

    def update_form_rgb(self, text, r, g, b):

        ncolor = RGBToPILColor((r, g, b))
        self.update_form_color_ex(text, ncolor, r, g, b)

    def update_form_color_ex(self, text, ncolor, r, g, b):

        #let's get HSL like here https://www.rapidtables.com/convert/color/rgb-to-hsl.html
        h, l, s = RGBToHLS(r, g, b)
        h = float_to_degrees(h)
        l = float_to_percent(l)
        s = float_to_percent(s)

        dlg_proc(self.h_dlg_color, DLG_CTL_PROP_SET, name='panel_color', prop={
                'color': ncolor,
                })

        dlg_proc(self.h_dlg_color, DLG_CTL_PROP_SET, name='label_text', prop={
                'cap': text,
                })

        dlg_proc(self.h_dlg_color, DLG_CTL_PROP_SET, name='label_rgb', prop={
                'cap': 'rgb(%d, %d, %d)' % (r, g, b),
                })

        dlg_proc(self.h_dlg_color, DLG_CTL_PROP_SET, name='label_hls', prop={
                'cap': 'hsl(%s, %s, %s)' % (h, s, l),
                })


    def update_form_pic(self, text):

        fn = self.get_pic_filename(text)
        if not os.path.isfile(fn):
            return False

        image_proc(self.h_img, IMAGE_LOAD, fn)
        size_x, size_y = image_proc(self.h_img, IMAGE_GET_SIZE)
        if not size_x:
            return False

        dlg_proc(self.h_dlg_pic, DLG_CTL_PROP_SET, name='label_text', prop={
                'cap': '%d×%d' % (size_x, size_y),
                })
        return True


    def update_form_ent(self, text):

        dlg_proc(self.h_dlg_ent, DLG_CTL_PROP_SET, name='label_text', prop={
                'cap': html_parser.unescape(text),
                })
        return True


    def get_pic_filename(self, text):

        #for Windows
        if os.sep != '/':
            text = text.replace('/', os.sep)

        dirname = os.path.dirname(ed.get_filename())
        return os.path.join(dirname, text)
