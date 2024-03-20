#!/usr/bin/env python3
# Created by Master on 3/16/2024

import argparse
import os

import iml

CD_SECTOR_SIZE = 0x930
DVD_SECTOR_SIZE = 0x800


# noinspection PyComparisonWithNone
def convert_to_cd_media(iml_cd: iml.IML, out_fp: str):
    print('CD is not yet supported!')

    # TODO
    return


# noinspection PyComparisonWithNone
def convert_to_dvd_media(iml_dvd: iml.IML, iml_dual_layer: iml.IML, out_fp: str):
    if not out_fp.lower().endswith('.iso'):
        print(f'Selected output disc image \"{out_fp}\" does not end with \".iso\"?!')
        print('Automatically appending\n')
        out_fp += '.iso'
        pass

    if os.path.exists(out_fp):
        if not os.path.isfile(out_fp):
            print(f'File path \"{out_fp}\" is not a file?!')
            return
        mode = 'w+'
        pass
    else:
        mode = 'x'
        pass

    if iml_dual_layer != None:
        print('\nWarning: DVD-9 support is experimental and may result in a bad image!')
        print('Please report any issues!\n')
        pass

    print('Creating DVD ISO....')

    with open(out_fp, mode=f'{mode}b') as io_iso:
        for i in range(0, len(iml_dvd.loc.entries)):
            entry = iml_dvd.loc.entries[i]
            if i == 0 and entry.start != 0:  # wtf
                print('Bad source in first loc entry!')
                print('Cannot be other than zero!')
                print('Aborting operation!')
                return

            if not os.path.exists(entry.source):
                print(f'File \"{entry.source}\" does not exist!')
                print('Aborting operation!')
                return

            io_iso.seek(entry.start * DVD_SECTOR_SIZE)
            with open(entry.source, mode='rb+') as io_entry:
                if entry.source_offset != None:
                    io_entry.seek(entry.source_offset)
                    pass
                io_iso.write(
                    io_entry.read()
                )
                pass
            del io_entry
            del entry
            continue
        del i

        # dual layer iso has first 0x8000 bytes removed, then glued on at the end of the first layer
        if iml_dual_layer != None:
            dual_layer_break = io_iso.tell()

            print('Done creating first layer.\nNow creating second layer...')

            for i in range(0, len(iml_dual_layer.loc.entries)):
                entry: iml.IML.Loc.Entry = iml_dual_layer.loc.entries[i]

                to_seek = (int(dual_layer_break / DVD_SECTOR_SIZE) + entry.start) * DVD_SECTOR_SIZE
                if i > 0:
                    to_seek -= (16 * DVD_SECTOR_SIZE)
                    pass

                io_iso.seek(to_seek)

                with open(entry.source, mode='rb+') as io_entry:
                    if i == 0:
                        io_entry.seek(16 * DVD_SECTOR_SIZE)  # skip first 16 sectors in ims
                        pass
                    if entry.source_offset != None:
                        io_entry.seek(entry.source_offset)
                        pass
                    io_iso.write(
                        io_entry.read()
                    )
                    pass
                del io_entry
                del to_seek
                del entry
                continue
            del i
            pass
        print('Done creating ISO')
        pass
    return


# noinspection PyComparisonWithNone
def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--iml', required=True, type=str)
    arg_parser.add_argument('--iml_dl', required=False, type=str)
    arg_parser.add_argument('--out_disc_image', required=True, type=str)
    args = arg_parser.parse_args()

    iml_data = iml.IML.parse_iml(args.iml)
    if args.iml_dl != None:
        iml_dual_layer = iml.IML.parse_iml(args.iml_dl)
        pass
    else:
        iml_dual_layer = None
        pass

    if iml_data == None:
        print('Error parsing iml file?!')
        return

    if iml_data.sys.media == 'DVD':
        if iml_dual_layer == None and args.iml_dl != None:
            print('Couldn\'t parse second layer for DVD-9!')
            print('Failed to make dual layer DVD!')
            return
        convert_to_dvd_media(iml_data, iml_dual_layer, args.out_disc_image)
        pass
    elif iml_data.sys.media == 'CD':
        if iml_dual_layer != None:
            print('Dual layer iml was inputted, but CDs do not have a dual layer!')
            print('Exiting...')
            return
        convert_to_cd_media(iml_data, args.out_disc_image)
        return
    else:
        print(f'Invalid media \"{iml_data.sys.media}\"!')
        return
    return


if __name__ == '__main__':
    main()
    pass
