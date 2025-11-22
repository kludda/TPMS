# TPMS

Generates a mesh representing a **[Schoen gyroid](https://en.wikipedia.org/wiki/Gyroid)**, which is  is an infinitely connected **triply periodic minimal surface** discovered by Alan Schoen in 1970.

The exiting thing with the gyroid is the high surface area which makes it suitable for heat exchanger applications.

Parametric CAD software, e.g. SolidWorks, currently aren't suitable to draw these kind of surfaces so they need to be imported as mesh. 

This is, as far as I know, the only gyroid generator that does not rely on any other software than Python and Python packages. Please let me know if I'm wrong!

&#x2615; [Buy me a coffee :)](https://paypal.me/davidalind)

<p align="center">
<img src="images/gyroid_s40_r80_t1_cap_p2_sp0.png" />
</p>

### Alternatives
There are specialized softwares, e.g. Ansys nTopology, but it's not within reach for a single project or hobbyist. There is a "[volumetric lattice]( https://help.autodesk.com/view/fusion360/ENU/?guid=SLD-VOLUMETRIC-PROPERTIES)" included in the Fusion 360 design extension, but it looks like it is only skeletal.

[TPMSgen](https://github.com/albertforesg/TPMSgen) seems to be a very nice tool, but it depends on Blender.

<a name="inital_setup"></a>
## Inital setup

You need python installed. ([Python doc on Windows](https://docs.python.org/3/using/windows.html))

Clone repo or download and unzip https://github.com/kludda/TPMS
```
git clone https://github.com/kludda/TPMS.git
```
Enter `TPMS` folder using a shell e.g. Windows Powershell.

Not necessary but recommended; set up a [virtual environment for python](https://docs.python.org/3/library/venv.html) and activate (commands are for Windows, if you're on *nix you probably know already):

```
python -m venv .\.venv 
.\.venv\Scripts\activate
```

Install required packages:
```
python -m pip install -r requirements.txt
```

(You can skip `matplotlib` if you don't want to use `--png` or `--show`.)


## CLI

```
usage: generate.py [-h] --conf CONF [--stl] [--txt] [--png] [--show] [--loglevel LOGLEVEL]

options:
  -h, --help   show this help message and exit
  --stl        Save mesh to STL. Will overwrite if exist.
  --txt        Save conf and extra data to a text file as prettyfied json. Will overwrite if exist.
  --png        Save a PNG. Will overwrite if exist.
  --show       Show generated mesh in a window.
  --log LOG    DEBUG, INFO, WARNING

required:
  --conf CONF  Your configuration file.
```

* **--conf CONF** Your [YAML configuration file](#conf) containing the parameters of the mesh to generate.

* **--stl** Save the generated mesh to an [STL](https://en.wikipedia.org/wiki/STL_(file_format)). Will overwrite existing file.

* **--txt** Save configuration and some extra data to a text file as prettyfied json. Useful if you generate multiple meshes and want to know what parameters you used. Will overwrite existing file.

* **--png** Save a image ISO view of the PNG. Useful if you have multiple mesh files and quickly want to find the one to import. Will overwrite existing file. The tool currently use Matplotlib to create this image. Matplotlib performance for this is low, generating images for high resolution will be very slow.

* **--show** Show generated mesh in an interactive view. The tool currently use Matplotlib to create interactive view. Matplotlib performance for this is low, viewing high resolution mesh will be very slow.

* **--log LOGLEVEL** DEBUG, INFO, WARNING (default). The tool is quiet unless setting loglevel.


Example usage:
```
python generate.py --log INFO --conf gyroid.yaml --txt --png --stl
```

<a name="conf"></a>
## Configuration file

```
metadata:
  description: Gyroid example
  filename: gyroid_example

mesh:
  size: 40
  resolution: 40
  thicken: 1
  cap extremes:
  heat exchanger: 1
  
gyroid:
  periodicity: 2
  strut param: 0
```

* **metadata:**
  * **filename:** Required. The filename, without ending, to use for the generated files.
  * You can add any tag, like `description`, and they will be saved in the text file.

* **mesh:**
  * **size:** Required. Size of geometry. The tool will generate a cube with equal length sides.
  * **resolution:** Required. The resolution of the entire size. If too coarse the mesh will not generate properly. If too fine the mesh will be unnecessarily large and difficult to post process. To avoid rounding issues, ensure (size / resolution) have a finite number of decimals.  

  * **thicken:** Optional. Thickness in size units. Offset the surface (thicken / 2 ) to each side.

  * **cap extremes:** Optional. Puts a "cap" on the surface at the bounding box extremes. This makes an infinitely connected surface a solid.  
  Use with `thicken` to make a shell.  
  Use without `thicken` to make a skeletal.

  * **heat exchanger:** Optional. Creates alternating lids on volumes in X and Y. Caps the entire face in Z. Thickness in size units. Offset the surface (`heat exchanger / 2`) to each side. Cannot be used together with `thicken` or `cap extremes`. The lids will have a thickness of `round(heat exchanger / (size / resolution))`. `size` is the size of the gyroid solid, the lids are outside `size`. Origin of gyroid solid is at 0,0,0.

* **gyroid:**
  * **periodicity:** Required. The number of periods within the cube.
  * **strut param:** Required. 0 ➝ a gyroid, <0< ➝ gyroid-like. In practice `strut param` ≠ 0 makes the volumes in the gyroid  asymmetrical. The surfaces overlap somewhere around +/- 0.95.

Mesh resolution starting point for gyroid: `periodicity` × 20. If e.g. thickening with small thickness; resolutions needs to be higher.

>Note: The "caps" will be convex. Therefore the bounding box is bigger than `size` if using `cap extremes`. The cube origin is still at 0,0,0.


## Examples

### Gyroid surface

```
mesh:
  size: 40
  resolution: 40
gyroid:
  periodicity: 2
  strut param: 0
```

<img src="images/gyroid_s40_r40_p2_sp0.png" />


### Offset gyroid surface

```
mesh:
  size: 40
  resolution: 40
  thicken: 1.2
gyroid:
  periodicity: 2
  strut param: 0
```

<img src="images/gyroid_s40_r40_t2_p2_sp0.png" />

### Thickened gyroid surface

```
mesh:
  size: 40
  resolution: 40
  thicken: 2
  cap extremes:
gyroid:
  periodicity: 2
  strut param: 0
```

<img src="images/gyroid_s40_r40_t2_cap_p2_sp0.png" />

### Skeletal gyroid-like surface

```
mesh:
  size: 40
  resolution: 40
  cap extremes:
gyroid:
  periodicity: 2
  strut param: -0.7
```

<img src="images/gyroid_s40_r40_cap_p2_sp-0.7.png" />

### Gyroid heat exchanger

```
mesh:
  size: 40
  resolution: 80
  heat exchanger: 1
gyroid:
  periodicity: 2
  strut param: 0
```

<img src="images/gyroid_s40_r80_heatexchanger1_p2_sp0.png" />


## Future features

Possible future features. Not actively development at the moment.

* Done ~~Generate separate alternating caps on thickened geometry to close of hot/cold side volumes. (I accidentally generated the surfaces for this during development so should be possible.)~~

* Geometry with non-equal sides. This has a value if the above is developed. Else just cut in post process.

# Acknowledgment and background

I've seen these gyroids before and when randomly watching [this YouTube video](https://www.youtube.com/watch?v=WI4CQ3qOETc) I got curious if one could use any programmatic software like [OpenSCAD](https://openscad.org/) to make the gyroid lattice ("no", as it turns out).

While searching I found [this post](https://forum.freecad.org/viewtopic.php?p=233282#p233282) (also linking to [this](https://kenbrakke.com/evolver/examples/periodic/periodic.html) and [this](https://www.fleckmech.org/papers/302.pdf)) and started hacking. When almost done I also found [TPMSgen](https://github.com/albertforesg/TPMSgen), luckily too late else I wouldn't have done it myself, learning new things :)

