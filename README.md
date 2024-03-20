# iml2iso

Converts PS2 `.iml`  to `.iso`

Supports DVD-5 and DVD-9 (experimental!) images

Do **_NOT_** ask where to get CD DVD-ROM Generator.

## Usage:

### Program Arguments:
- `--iml`
  - The input `.iml` file
- `--out_disc_image`
  - The output disc image
  - DVD-5 and DVD-9 images use the `.iso` extension.<br/>
This will automatically be appended if none is found or if used incorrectly

### Examples:
- DVD-5:
  - `py -3 main.py --iml=Test_DVD-5.iml --out_disc_image=Test_DVD-5.iso`
- DVD-9:
  - `py -3 main.py --iml=Test_DVD-9.0.iml --iml_dl=Test_DVD-9.1.iml --out_disc_image=Test_DVD-9.iso`

## Requirements:
* Python 3.12
