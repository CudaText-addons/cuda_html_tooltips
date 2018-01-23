Plugin for CudaText.
It works in HTML/CSS/JavaScript files (any lexer name with words "HTML", "CSS", "JavaScript").

It finds HTML color tokens: #rgb #rrggbb; and adds colored tooltips for them.
It finds HTML picture refs: <img src="...">; and adds picture tooltips for filenames.
(Internally, if finds any quoted picture filenames without testing tags.) 
When you move mouse cursor over found tokens, tooltip appears.

It finds tokens:
- on opening file,
- after text is changed + pause passed (CudaText option "py_change_slow").
If you're interested, what is HSL display, see
https://www.rapidtables.com/convert/color/rgb-to-hsl.html

Author: Alexey (CudaText)
License: MIT
