# iml2iso

Converts PS2 `.iml` generated to `.iso`

Only supports DVD-5 for now

Do **_NOT_** ask where to get CD DVD-ROM Generator.

## Usage:
- `--iml`
  - The input `.iml` file
- `--out_disc_image`
  - The output disc image
  - DVD-5 images use the `.iso` extension

### Examples:
`py -3 main.py --iml=Test_DVD-5.iml --out_disc_image=Test_DVD-5.iso`

## Requirements:
* Python 3.12

## Note:
This was **NOT** reverse engineered by disassembling/decompiling the Sony cdvdgen tool
nor Gnie's iml2iso tool
