import re
import json
import os
import html
from cudatext import *
from .colorcodes import *

fn_ini = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_html_tooltips.ini')
MY_TAG = 101 #uniq value for all plugins with ed.hotspots()

LEXERS_CSS = 'CSS,SCSS,Sass,LESS'
REGEX_COLORS = r'(\#[0-9a-f]{3}\b)|(\#[0-9a-f]{6}\b)'
REGEX_RGB = r'\brgba?\(\s*(\d+%?)\s*[,\s]\s*(\d+%?)\s*[,\s]\s*(\d+%?)\s*([,\s/]\s*[\d\.%?]+\s*)?\)'
REGEX_HSL = r'\bhsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)'
REGEX_PIC = r'(\'|")[^\'"]+?\.(png|gif|jpg|jpeg|bmp|ico|webp)\1'
REGEX_PIC_CSS = r'\([^\'"\(\)]+?\.(png|gif|jpg|jpeg|bmp|ico|webp)\)'
REGEX_ENT = r'&\#?\w+;'

re_colors_compiled = re.compile(REGEX_COLORS, re.I)
re_rgb_compiled = re.compile(REGEX_RGB, 0)
re_hsl_compiled = re.compile(REGEX_HSL, 0)
re_pic_compiled = re.compile(REGEX_PIC, re.I)
re_pic_css_compiled = re.compile(REGEX_PIC_CSS, re.I)
re_ent_compiled = re.compile(REGEX_ENT, 0)

FORM_COLOR_W = 170
FORM_COLOR_H = 25
FORM_PIC_W_MAX = 270
FORM_PIC_W_MIN = 50
FORM_PIC_H_MAX = 220
FORM_PIC_H_MIN = 50
FORM_ENT_W = 50
FORM_ENT_H = 50
FORM_ENT_FONT_SIZE = 28
FORM_GAP = 4
FORM_GAP_OUT = 0
FORM_GAP_OUT_COLOR = 0 #-1
FORM_COLOR_KEEP = False
COLOR_FORM_BACK = 0x505050
COLOR_FORM_FONT = 0xE0E0E0
COLOR_FORM_FONT2 = 0x40E0E0
COLOR_FORM_PANEL_BORDER = 0xFFFFFF
MAX_LINES = 5000

def str2color(s):
    perc = s.endswith('%')
    if perc:
        s = s[:-1]
    n = int(s)
    if perc:
        n = n*255//100
    return n


class Command:

    def __init__(self):

        self.load_config()
        self.init_form_color()
        self.init_form_pic()
        self.init_form_ent()

    def on_change_slow(self, ed_self):

        self.find_hotspots(ed_self)

    def on_open(self, ed_self):

        self.find_hotspots(ed_self)

    def find_hotspots(self, ed):

        ed.hotspots(HOTSPOT_DELETE_BY_TAG, tag=MY_TAG)
        count = 0
        use_count = min(ed.get_line_count(), MAX_LINES)

        for nline in range(use_count):
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
                        'r': str2color(item.group(1)),
                        'g': str2color(item.group(2)),
                        'b': str2color(item.group(3)),
                        'x': span[0],
                        'y': nline,
                        })

                ed.hotspots(HOTSPOT_ADD,
                            tag=MY_TAG,
                            tag_str=data,
                            pos=(span[0], nline, span[1], nline)
                            )
                count += 1

            #find hsl
            for item in re_hsl_compiled.finditer(line):
                span = item.span()
                data = json.dumps({
                        'hsl': item.group(0),
                        'h': int(item.group(1)),
                        's': int(item.group(2)),
                        'l': int(item.group(3)),
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

            #same for CSS lexers
            lexer = ed.get_prop(PROP_LEXER_FILE)
            if ed.get_filename() and (','+lexer+',' in ','+LEXERS_CSS+','):
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


    def dlgcolor_mouse_exit(self, id_dlg, id_ctl, data='', info=''):

        if not self.is_mouse_in_form(id_dlg):
            dlg_proc(id_dlg, DLG_HIDE)


    def on_hotspot(self, ed_self, entered, hotspot_index):

        if not entered:
            allow = FORM_COLOR_KEEP and self.is_mouse_in_form(self.h_dlg_color)
            if allow: return
            self.hide_forms()

        else:
            self.hide_forms()
            hotspot = ed_self.hotspots(HOTSPOT_GET_LIST)[hotspot_index]
            if hotspot['tag'] != MY_TAG: return

            data = json.loads(hotspot['tag_str'])

            text = data.get('color', '')
            if text:
                self.update_form_color(text)
                h_dlg = self.h_dlg_color
            else:
                text = data.get('pic', '')
                if text:
                    if not self.update_form_pic(ed_self, text): return
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
                            text = data.get('hsl', '')
                            if text:
                                self.update_form_hsl(text, data['h'], data['s'], data['l'])
                                h_dlg = self.h_dlg_color
                            else:
                                return

            prop = dlg_proc(h_dlg, DLG_PROP_GET)
            form_w = prop['w']
            form_h = prop['h']

            pos_x = data['x']
            pos_y = data['y']
            pos = ed_self.convert(CONVERT_CARET_TO_PIXELS, x=pos_x, y=pos_y)

            gap_out = FORM_GAP_OUT_COLOR if h_dlg==self.h_dlg_color else FORM_GAP_OUT
            cell_size = ed_self.get_prop(PROP_CELL_SIZE)
            ed_coord = ed_self.get_prop(PROP_COORDS)
            ed_size_x = ed_coord[2]-ed_coord[0]
            ed_size_y = ed_coord[3]-ed_coord[1]
            hint_x = pos[0]
            hint_y = pos[1] + cell_size[1] + gap_out

            #no space on bottom?
            if hint_y + form_h > ed_size_y:
                y_ = pos[1] - form_h - gap_out
                if y_>=0:
                    hint_y = y_

            #no space on right?
            if hint_x + form_w > ed_size_x:
                hint_x = ed_size_x - form_w

            dlg_proc(h_dlg, DLG_PROP_SET, prop={
                    'p': ed_self.h, #set parent to Editor handle
                    'x': hint_x,
                    'y': hint_y,
                    })
            dlg_proc(h_dlg, DLG_SHOW_NONMODAL)
            if h_dlg==self.h_dlg_color:
                self.update_form_color_size()


    def hide_forms(self):

        dlg_proc(self.h_dlg_color, DLG_HIDE)
        dlg_proc(self.h_dlg_pic, DLG_HIDE)
        dlg_proc(self.h_dlg_ent, DLG_HIDE)


    def init_form_color(self):

        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg_color = h

        dlg_proc(h, DLG_PROP_SET, prop={
                'w': FORM_COLOR_W+2*FORM_GAP,
                'border': False,
                'color': COLOR_FORM_BACK,
                'on_mouse_exit': self.dlgcolor_mouse_exit,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'colorpanel')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'panel_color',
                'align': ALIGN_TOP,
                'sp_a': FORM_GAP,
                'h': FORM_COLOR_H,
                'ex0': 1,
                'ex1': 0x808080,
                'ex2': 0x202020,
                'ex3': COLOR_FORM_PANEL_BORDER,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_text',
                'cap': '?',
                'font_color': COLOR_FORM_FONT2,
                'align': ALIGN_TOP,
                'sp_l': FORM_GAP,
                'sp_r': FORM_GAP,
                'sp_b': FORM_GAP,
                'y': 200,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_rgb',
                'cap': '??',
                'font_color': COLOR_FORM_FONT,
                'align': ALIGN_TOP,
                'sp_l': FORM_GAP,
                'sp_r': FORM_GAP,
                'sp_b': FORM_GAP,
                'y': 220,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_hls',
                'cap': '??',
                'font_color': COLOR_FORM_FONT,
                'align': ALIGN_TOP,
                'sp_l': FORM_GAP,
                'sp_r': FORM_GAP,
                'sp_b': FORM_GAP,
                'y': 240,
                })


    def init_form_pic(self):

        h = dlg_proc(0, DLG_CREATE)
        self.h_dlg_pic = h

        dlg_proc(h, DLG_PROP_SET, prop={
                'w': FORM_PIC_W_MAX,
                'h': FORM_PIC_H_MAX,
                'border': False,
                'color': COLOR_FORM_BACK,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'label')
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'label_text',
                'cap': '??',
                'font_color': COLOR_FORM_FONT,
                'align': ALIGN_TOP,
                'sp_a': FORM_GAP,
                })

        n = dlg_proc(h, DLG_CTL_ADD, 'image')
        self.h_img = dlg_proc(h, DLG_CTL_HANDLE, index=n)
        dlg_proc(h, DLG_CTL_PROP_SET, index=n, prop={
                'name': 'img',
                'align': ALIGN_CLIENT,
                'sp_l': FORM_GAP,
                'sp_r': FORM_GAP,
                'sp_b': FORM_GAP,
                'ex0': True, #center
                'ex1': True, #stretch
                'ex2': True, #stretch in
                'ex3': False, #stretch out
                'ex4': True, #keep origin x
                'ex5': True, #keep origin y
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

    def update_form_hsl(self, text, h, s, l):

        ncolor, r, g, b = hsl_to_rgb(h, s, l)
        self.update_form_color_ex(text, ncolor, r, g, b, h/360, s/100, l/100)

    def update_form_color_size(self):

        h_dlg = self.h_dlg_color
        prop = dlg_proc(h_dlg, DLG_CTL_PROP_GET, name='label_hls')
        need_size = prop['y']+prop['h']+FORM_GAP
        dlg_proc(h_dlg, DLG_PROP_SET, prop={'h': need_size})

    def update_form_color_ex(self, text, ncolor, r, g, b, h=-1, s=-1, l=-1):

        h_dlg = self.h_dlg_color

        #let's get HSL like here https://www.rapidtables.com/convert/color/rgb-to-hsl.html
        if h == -1:
            h, l, s = RGBToHLS(r, g, b)

        h = float_to_degrees(h)
        l = float_to_percent(l)
        s = float_to_percent(s)

        dlg_proc(h_dlg, DLG_CTL_PROP_SET, name='panel_color', prop={
                'color': ncolor,
                })

        dlg_proc(h_dlg, DLG_CTL_PROP_SET, name='label_text', prop={
                'cap': text,
                })

        dlg_proc(h_dlg, DLG_CTL_PROP_SET, name='label_rgb', prop={
                'cap': 'rgb(%d, %d, %d)' % (r, g, b),
                })

        dlg_proc(h_dlg, DLG_CTL_PROP_SET, name='label_hls', prop={
                'cap': 'hsl(%s, %s, %s)' % (h, s, l),
                })


    def update_form_pic(self, ed, text):

        fn = self.get_pic_filename(ed, text)
        if not os.path.isfile(fn):
            return False

        image_proc(self.h_img, IMAGE_LOAD, fn)
        size_x, size_y = image_proc(self.h_img, IMAGE_GET_SIZE)
        if not size_x or not size_y:
            return False

        dlg_proc(self.h_dlg_pic, DLG_CTL_PROP_SET, name='label_text', prop={
                'cap': '%d×%d' % (size_x, size_y),
                })

        label_h = dlg_proc(self.h_dlg_pic, DLG_CTL_PROP_GET, name='label_text')['h']

        #ratio_xy = size_x/size_y
        #if size_x<FORM_PIC_W_MAX and size_y<FORM_PIC_H_MAX:
        form_w = min(FORM_PIC_W_MAX, max(FORM_PIC_W_MIN, size_x)) + 2*FORM_GAP
        form_h = min(FORM_PIC_H_MAX, max(FORM_PIC_H_MIN, size_y)) + 3*FORM_GAP + label_h

        dlg_proc(self.h_dlg_pic, DLG_PROP_SET, prop={
            'w': form_w,
            'h': form_h,
            })

        return True


    def update_form_ent(self, text):

        s = html.unescape(text)
        if s==chr(10):
            s = 'lf'
        elif s==chr(13):
            s = 'cr'
        elif s==chr(9):
            s = 'tab'
        elif s==chr(0xA0):
            s = 'sp'

        dlg_proc(self.h_dlg_ent, DLG_CTL_PROP_SET, name='label_text', prop={
                'cap': s,
                })
        return True


    def get_pic_filename(self, ed, text):

        #for Windows
        if os.sep != '/':
            text = text.replace('/', os.sep)

        dirname = os.path.dirname(ed.get_filename())
        return os.path.join(dirname, text)


    def is_mouse_in_form(self, h_dlg):

        prop = dlg_proc(h_dlg, DLG_PROP_GET)
        if not prop['vis']: return False
        w = prop['w']
        h = prop['h']

        x, y = app_proc(PROC_GET_MOUSE_POS, '')
        x, y = dlg_proc(h_dlg, DLG_COORD_SCREEN_TO_LOCAL, index=x, index2=y)

        return 0<=x<w and 0<=y<h


    def edit_config(self):

        ini_write(fn_ini, 'colors', 'back', PILColorToHTMLColor(COLOR_FORM_BACK))
        ini_write(fn_ini, 'colors', 'font', PILColorToHTMLColor(COLOR_FORM_FONT))
        ini_write(fn_ini, 'colors', 'font2', PILColorToHTMLColor(COLOR_FORM_FONT2))
        ini_write(fn_ini, 'colors', 'panel_border', PILColorToHTMLColor(COLOR_FORM_PANEL_BORDER))

        ini_write(fn_ini, 'op', 'lexers_css', LEXERS_CSS)

        ini_write(fn_ini, 'op', 'color_size_x', str(FORM_COLOR_W))
        ini_write(fn_ini, 'op', 'color_size_y', str(FORM_COLOR_H))

        ini_write(fn_ini, 'op', 'entity_size_x', str(FORM_ENT_W))
        ini_write(fn_ini, 'op', 'entity_size_y', str(FORM_ENT_H))
        ini_write(fn_ini, 'op', 'entity_font_size', str(FORM_ENT_FONT_SIZE))

        ini_write(fn_ini, 'op', 'pic_size_x_max', str(FORM_PIC_W_MAX))
        ini_write(fn_ini, 'op', 'pic_size_x_min', str(FORM_PIC_W_MIN))
        ini_write(fn_ini, 'op', 'pic_size_y_max', str(FORM_PIC_H_MAX))
        ini_write(fn_ini, 'op', 'pic_size_y_min', str(FORM_PIC_H_MIN))

        ini_write(fn_ini, 'op', 'max_lines', str(MAX_LINES))

        if os.path.isfile(fn_ini):
            file_open(fn_ini)
        else:
            msg_status('Cannot find file: '+fn_ini)


    def load_config(self):

        global LEXERS_CSS

        global COLOR_FORM_BACK
        global COLOR_FORM_FONT
        global COLOR_FORM_FONT2
        global COLOR_FORM_PANEL_BORDER

        global FORM_COLOR_W
        global FORM_COLOR_H

        global FORM_ENT_W
        global FORM_ENT_H
        global FORM_ENT_FONT_SIZE

        global FORM_PIC_W_MAX
        global FORM_PIC_W_MIN
        global FORM_PIC_H_MAX
        global FORM_PIC_H_MIN

        global MAX_LINES

        LEXERS_CSS = ini_read(fn_ini, 'op', 'lexers_css', LEXERS_CSS)

        COLOR_FORM_BACK = HTMLColorToPILColor(ini_read(fn_ini, 'colors', 'back', PILColorToHTMLColor(COLOR_FORM_BACK)))
        COLOR_FORM_FONT = HTMLColorToPILColor(ini_read(fn_ini, 'colors', 'font', PILColorToHTMLColor(COLOR_FORM_FONT)))
        COLOR_FORM_FONT2 = HTMLColorToPILColor(ini_read(fn_ini, 'colors', 'font2', PILColorToHTMLColor(COLOR_FORM_FONT2)))
        COLOR_FORM_PANEL_BORDER = HTMLColorToPILColor(ini_read(fn_ini, 'colors', 'panel_border', PILColorToHTMLColor(COLOR_FORM_PANEL_BORDER)))

        FORM_COLOR_W = int(ini_read(fn_ini, 'op', 'color_size_x', str(FORM_COLOR_W)))
        FORM_COLOR_H = int(ini_read(fn_ini, 'op', 'color_size_y', str(FORM_COLOR_H)))

        FORM_ENT_W = int(ini_read(fn_ini, 'op', 'entity_size_x', str(FORM_ENT_W)))
        FORM_ENT_H = int(ini_read(fn_ini, 'op', 'entity_size_y', str(FORM_ENT_H)))
        FORM_ENT_FONT_SIZE = int(ini_read(fn_ini, 'op', 'entity_font_size', str(FORM_ENT_FONT_SIZE)))

        FORM_PIC_W_MAX = int(ini_read(fn_ini, 'op', 'pic_size_x_max', str(FORM_PIC_W_MAX)))
        FORM_PIC_W_MIN = int(ini_read(fn_ini, 'op', 'pic_size_x_min', str(FORM_PIC_W_MIN)))
        FORM_PIC_H_MAX = int(ini_read(fn_ini, 'op', 'pic_size_y_max', str(FORM_PIC_H_MAX)))
        FORM_PIC_H_MIN = int(ini_read(fn_ini, 'op', 'pic_size_y_min', str(FORM_PIC_H_MIN)))

        MAX_LINES = int(ini_read(fn_ini, 'op', 'max_lines', str(MAX_LINES)))
