#!/usr/bin/env python3
# Created by Master on 4/3/2024

import io
import os
import pathlib

import iml

DVD_SECTOR_SIZE = 0x800  # 2048


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

    print('Creating DVD ISO...\n')

    with open(out_fp, mode=f'{mode}b') as io_iso:
        for i in range(0, len(iml_dvd.loc.entries)):
            entry = iml_dvd.loc.entries[i]
            entry_fp = entry.source
            if i == 0 and entry.start != 0:  # wtf
                print('Bad source in first loc entry!')
                print('Cannot be other than zero!')
                print('Aborting operation!')
                return
            if not os.path.exists(entry_fp):
                # attempt to use file in local directory
                print(f'File \"{entry_fp}\" does not exist!')
                print('Attempting to look in same directory as iml file...')
                entry_fp = os.path.join(pathlib.Path(iml_dvd.fp).parent, os.path.basename(entry.source))
                if not os.path.exists(entry_fp):
                    print(f'File \"{entry_fp}\" still does not exist!')
                    print('Aborting operation!')
                    return
                else:
                    print(f'Found in \"{entry_fp}\"\n')
                    pass
                pass
            if entry.mode != '0.0':  # always expect 0.0
                print(f'Unexpected mode set for entry {i}!')
                return

            io_iso.seek(entry.start * DVD_SECTOR_SIZE, io.SEEK_SET)
            with open(entry_fp, mode='rb+') as io_entry:
                if entry.source_offset != None:
                    io_entry.seek(entry.source_offset, io.SEEK_SET)
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

                io_iso.seek(to_seek, io.SEEK_SET)

                with open(entry.source, mode='rb+') as io_entry:
                    if not os.path.exists(entry.source):
                        print(f'File \"{entry.source}\" does not exist!')
                        print('Aborting operation!')
                        return
                    if i == 0:
                        io_entry.seek(16 * DVD_SECTOR_SIZE, io.SEEK_SET)  # skip first 16 sectors in ims
                        pass
                    if entry.source_offset != None:
                        io_entry.seek(entry.source_offset, io.SEEK_SET)
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
