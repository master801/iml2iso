# iml2iso

Converts PS2 `.iml`  to `.bin` and `.iso`

Supports CD (experimental!), DVD-5 and DVD-9 (experimental!) images

Do **_NOT_** ask where to get CD DVD-ROM Generator.

## Usage:

### Program Arguments:
- `--iml`
  - The input `.iml` file
- `--iml_dl`
  - The `.iml` file for the second layer to create a DVD-9 image.<br>
Do **NOT**  use this for CD images.
- `--out_disc_image`
  - The output disc image
  - DVD-5 and DVD-9 images use the `.iso` extension.<br/>
This will automatically be appended if none is given or if used incorrectly.<br/>
CD images do not need a given extension and will automatically use bin+cue.

### Examples:
- CD:
  - `py -3 main.py --iml=Test_CD.iml --out_disc_image=Test_CD`
- DVD-5:
  - `py -3 main.py --iml=Test_DVD-5.iml --out_disc_image=Test_DVD-5.iso`
- DVD-9:
  - `py -3 main.py --iml=Test_DVD-9.0.iml --iml_dl=Test_DVD-9.1.iml --out_disc_image=Test_DVD-9.iso`

## Requirements:
* Python 3.12
* [fastcrc 0.3.0](https://pypi.org/project/fastcrc/0.3.0/) - For CD images
