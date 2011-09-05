Quake Live Firefox fix
======================

The goal of this script is to fix the Quake Live plugin in order to be able to play Quake Live with every Firefox version.

Required software
-----------------
* Python (If you're running Linux, then you might have it)

Installation
------------
* Download the XPI plugin on the [Quake Live website](http://www.quakelive.com/)
* Download the script [here](https://github.com/samyboy/qlive_ff_fix/raw/master/qlive_ff_fix.py)
* Make the script executable with `chmod +x qlive_ff_fix.py`

Usage
-----

Here are some examples of the usage of the script:

Creates a Firefox Plugin compatible up to version 7 (this is the default, this is probably what you want).

    ./qlive_ff_fix.py QuakeLivePlugin_433.xpi

Create a Firefox Plugin compatible up to version 5.0

    ./qlive_ff_fix.py --ff_version=5.0 QuakeLivePlugin_433.xpi


All the options are available with the `--help` option:

When the plugin is fixed, just open it with firefox, restart your browser and enjoy your game.
