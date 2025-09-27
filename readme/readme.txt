Plugin for CudaText.
It works for lexers:
- HTML and any lexer name with word "HTML"
- CSS, SCSS, Sass, LESS
- Markdown

When you move mouse cursor over supported fragments, tooltip-window appears.
It finds fragments:
- on opening file,
- after text is changed + pause passed (CudaText option "py_change_slow").


Features
--------

1) It finds HTML color values: 
  #RGB 
  #RRGGBB
  rgb(n, n, n)
  rgba(n, n, n, n)
  hsl(n, n, n)
  and adds colored tooltips for them.

2) It finds HTML picture refs: src="..." or href="..."; and adds picture tooltips for filenames.
  Internally, it finds any quoted picture filenames (png, gif, jpeg, bmp, ico) without testing tags.
  Online links (http:, https:) are not supported.

3) It finds HTML entities like &copy; &amp; etc, and shows Unicode tooltips for them.

4) In CSS-based lexers, it finds filenames in special format: in brackets, not in quotes.
To tell plugin, which lexers are CSS-based, edit:
- install.inf, field "lexers=" (option is in install.inf to speedup app on other files)
- plugin option "lexers_css", it's in config file.

5) In Markdown lexer, it finds image links, both local and URLs:
![alt text](a.jpg "title a1")              #relative path
![alt text](dir1/b.jpg "title a2")         #relative path
![alt text](C:\work\dir\d.jpeg "title a3") #absolute path
![alt text](https://example.com/img.jpg)   #URL


Config
------

To edit config, call main menu item:
"Options / Settings-plugins / HTML Tooltips / Config".


Sidenotes
---------

If you're interested, what is HSL display, see
https://www.rapidtables.com/convert/color/rgb-to-hsl.html


About
-----

Author: Alexey Torgashin (CudaText)
License: MIT
