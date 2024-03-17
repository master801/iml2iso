#!/usr/bin/env python3
# Created by Master on 3/16/2024

import os
import argparse

import iml

SECTOR_SIZE = 0x800


# noinspection PyComparisonWithNone
def convert_to_dvd_iso(iml_data: iml.IML, out_fp: str):
    if os.path.exists(out_fp):
        if not os.path.isfile(out_fp):
            print(f'File path \"{out_fp}\" is not a file?!')
            return
        mode = 'w+'
        pass
    else:
        mode = 'x'
        pass

    with open(out_fp, mode=f'{mode}b') as io_iso:
        for i in range(0, len(iml_data.loc.entries)):
            entry = iml_data.loc.entries[i]
            if i == 0 and entry.start != 0:  # wtf
                print('Bad source in first loc entry!')
                print('Cannot be other than zero!')
                print('Aborting operation!')
                return

            if not os.path.exists(entry.source):
                print(f'File \"{entry.source}\" does not exist!')
                print('Aborting operation!')
                return

            io_iso.seek(entry.start * SECTOR_SIZE)
            with open(entry.source, mode='rb+') as io_entry:
                if entry.source_offset != None:
                    io_entry.seek(entry.source_offset)
                    pass
                io_iso.write(
                    io_entry.read()
                )
                pass

            end_seek = entry.end * SECTOR_SIZE
            if io_iso.tell() != end_seek: # bad seek?
                io_iso.seek(end_seek)  # re-seek
                pass
            continue
        pass
    return


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--iml', required=True, type=str)
    arg_parser.add_argument('--out_disc_image', required=True, type=str)
    args = arg_parser.parse_args()

    iml_data = iml.IML.parse_iml(args.iml)

    if iml_data.sys.target != 'PS2':
        print('Set target is other than \"PS2\"')
        print('Operation is invalid!')
        return

    if iml_data.sys.media == 'DVD':  # TODO support dual-layer images
        convert_to_dvd_iso(iml_data, args.out_disc_image)
        pass
    elif iml_data.sys.media == 'CD':
        # TODO
        print('TODO')
        print('This is a planned future feature and not yet implemented')
        return
    else:
        print(f'Cannot handle media \"{iml_data.sys.media}\"!')
        return
    return


if __name__ == '__main__':
    main()
    pass
