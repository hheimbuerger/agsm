AllegGameStatsMerger
====================

http://www.freeallegiance.org/forums/index.php?autocom=blog&blogid=10&req=editentry&eid=379&st=0

### Overview

AGSM can take stats screenshots you made from within Allegiance (using the 'PrntScr' button on the stats page) and merge them into one complete image.

Allegiance currently doesn't allow you to export game stats. What you can do is take screenshots of the stats pages. Unfortunately, only twelve players will be shown per screenshot. But if you want to post the stats of a game on the forum, you'll want to include all players.

The usual way the community handles this is to take screenshots of all the pages, then merge them manually in some raster image editor. AGSM automates the last of these steps. It will *not* help you take the actual screenshots, it can just combine them to one image.

If you follow some simple rules, you'll end up with pretty clean images.

### Usage

AGSM will automatically try to find 'clusters' in your screenshots. It will analyse when you took those screenshots and will group all those together taken in short intervals.

It will also analyse and reorder them depending on the position of the scrollbar included in the screenshots. Therefore, it doesn't matter in which order you take them. You can go upside down or downside up or even jump around like crazy.

The screenshots can also overlap. You can take them using page scrolling (clicking the scrollbar above or below the 'thumb'), but you'll get better results if you create them with a bit of overlap. The overlapping parts with automatically be removed.

### Implementation notes

The following libs and tools have been used:

* PIL (http://www.pythonware.com/products/pil/)
* wxPython (http://www.wxpython.org/)
* py2exe (http://www.py2exe.org/) to generate the executable
* Inno Setup (http://www.jrsoftware.org/isinfo.php) to generate the installer
* TextfileWrapper.py (included) to wrap the release notes

The buildfile (build.py) will prepare a release almost completely if all of the above tools are available. PIL, wxPython and py2exe need to be installed. Inno Setup has to be in the path.

When running the application locally without creating an executable, remember that the working directory has to be set to `/media`.