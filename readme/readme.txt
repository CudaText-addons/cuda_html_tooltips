Plugin for CudaText.
It works in HTML/CSS files (any lexer name with words "HTML", "CSS").
When you move mouse cursor over some fragments, tooltip appears.

1) It finds HTML color values: 
  #RGB 
  #RRGGBB
  rgb(n, n, n)
  rgba(n, n, n, n)  
  and adds colored tooltips for them.
2) It finds HTML picture refs: src="..." or href="..."; and adds picture tooltips for filenames.
  Internally, it finds any quoted picture filenames (png, gif, jpeg, bmp, ico) without testing tags.
  Online links (http:, https:) are not supported.
3) It finds HTML entities like &copy; &amp; etc, and adds Unicode tooltips for them.

It finds filenames in CSS files in special format: in brackets, not in quotes.
To tell plugin, which lexers are CSS based, edit:
- install.inf, field "lexers=" (option is in install.inf to speedup app on other files)
- plugin option "lexers_css", it's in config file.

To edit config, call "Options/ Settings-plugins/ HTML Tooltips/ Config".

It finds fragments:
- on opening file,
- after text is changed + pause passed (CudaText option "py_change_slow").

If you're interested, what is HSL display, see
https://www.rapidtables.com/convert/color/rgb-to-hsl.html


Author: Alexey (CudaText)
License: MIT
