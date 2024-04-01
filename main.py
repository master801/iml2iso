#!/usr/bin/env python3
# Created by Master on 3/16/2024

import argparse
import io
import os
import pathlib
import struct
import math

import iml


CD_SECTOR_SIZE = 0x930  # 2352
DVD_SECTOR_SIZE = 0x800  # 2048

CD_SYNC_PATTERN = (b'\x00\xFF\xFF\xFF'  # 12
                   b'\xFF\xFF\xFF\xFF'
                   b'\xFF\xFF\xFF\x00')

# Fucking bullshit BCD
fucking_bullshit_conversion = {
    0: struct.pack('<B', 0),
    1: struct.pack('<B', 1),
    2: struct.pack('<B', 2),
    3: struct.pack('<B', 3),
    4: struct.pack('<B', 4),
    5: struct.pack('<B', 5),
    6: struct.pack('<B', 6),
    7: struct.pack('<B', 7),
    8: struct.pack('<B', 8),
    9: struct.pack('<B', 9),
    10: bytes(b'\x10'),
    11: bytes(b'\x11'),
    12: bytes(b'\x12'),
    13: bytes(b'\x13'),
    14: bytes(b'\x14'),
    15: bytes(b'\x15'),
    16: bytes(b'\x16'),
    17: bytes(b'\x17'),
    18: bytes(b'\x18'),
    19: bytes(b'\x19'),
    20: bytes(b'\x20'),
    21: bytes(b'\x21'),
    22: bytes(b'\x22'),
    23: bytes(b'\x23'),
    24: bytes(b'\x24'),
    25: bytes(b'\x25'),
    26: bytes(b'\x26'),
    27: bytes(b'\x27'),
    28: bytes(b'\x28'),
    29: bytes(b'\x29'),
    30: bytes(b'\x30'),
    31: bytes(b'\x31'),
    32: bytes(b'\x32'),
    33: bytes(b'\x33'),
    34: bytes(b'\x34'),
    35: bytes(b'\x35'),
    36: bytes(b'\x36'),
    37: bytes(b'\x37'),
    38: bytes(b'\x38'),
    39: bytes(b'\x39'),
    40: bytes(b'\x40'),
    41: bytes(b'\x41'),
    42: bytes(b'\x42'),
    43: bytes(b'\x43'),
    44: bytes(b'\x44'),
    45: bytes(b'\x45'),
    46: bytes(b'\x46'),
    47: bytes(b'\x47'),
    48: bytes(b'\x48'),
    49: bytes(b'\x49'),
    50: bytes(b'\x50'),
    51: bytes(b'\x51'),
    52: bytes(b'\x52'),
    53: bytes(b'\x53'),
    54: bytes(b'\x54'),
    55: bytes(b'\x55'),
    56: bytes(b'\x56'),
    57: bytes(b'\x57'),
    58: bytes(b'\x58'),
    59: bytes(b'\x59'),
    60: bytes(b'\x60'),
    61: bytes(b'\x61'),
    62: bytes(b'\x62'),
    63: bytes(b'\x63'),
    64: bytes(b'\x64'),
    65: bytes(b'\x65'),
    66: bytes(b'\x66'),
    67: bytes(b'\x67'),
    68: bytes(b'\x68'),
    69: bytes(b'\x69'),
    70: bytes(b'\x70'),
    71: bytes(b'\x71'),
    72: bytes(b'\x72'),
    73: bytes(b'\x73'),
    74: bytes(b'\x74'),
    75: bytes(b'\x75'),
    76: bytes(b'\x76'),
    77: bytes(b'\x77'),
    78: bytes(b'\x78'),
    79: bytes(b'\x79'),
    80: bytes(b'\x80'),
}


def convert_to_time(cd_offset: int, seconds_offset: int = 2) -> iml.Time:
    """
    Big fuck you to whomever designed this bullshit system

    I cobbled this function together trying different shit. I don't know how this works, but it does.

    Random unlisted webpage with a formula
    https://www.isobuster.com/help/MSF_minutes_seconds_frames
    LBA = (((M*60)+S)*75+F)-150
    :param cd_offset: Offset in the CD file in sectors (2352)
    :param seconds_offset: How many seconds to offset (by default 2)
    :return:
    """
    sector = cd_offset / CD_SECTOR_SIZE
    minutes = math.floor((sector / 75) / 60)
    seconds = math.floor((sector / 75) % 60) + seconds_offset
    fractions = math.floor(sector % 75)
    return iml.Time(minutes, seconds, fractions)


# noinspection PyComparisonWithNone
def convert_to_cd_media(iml_cd: iml.IML, out_fp: str):
    """
    https://en.wikipedia.org/wiki/CD-ROM#CD-ROM_format
    """
    import fastcrc  # import locally so fastcrc isn't required to be installed for DVD ISOs

    if out_fp.lower().endswith('.bin'):
        print('Output file already has the \".bin\" extension?! This should not happen!')
        return
    elif out_fp.lower().endswith('.cue'):
        print('Output file already has the \".cue\" extension?! This should not happen!')
        return

    out_bin_fp = out_fp + '.bin'
    out_cue_fp = out_fp + '.cue'

    if os.path.exists(out_bin_fp):
        if not os.path.isfile(out_bin_fp):
            print(f'\"{out_bin_fp}\" exists but is not a file?!')
            return
        else:
            mode_bin = 'w+'
            pass
        pass
    else:
        mode_bin = 'x'
        pass
    if os.path.exists(out_cue_fp):
        if not os.path.isfile(out_cue_fp):
            print(f'\"{out_cue_fp}\" exists but is not a file?!')
            return
        else:
            mode_cue = 'w+'
            pass
        pass
    else:
        mode_cue = 'x'
        pass

    if len(iml_cd.cue.tracks) != 4:  # 00, 01, 01, AA
        print('IML has an unexpected amount of tracks!')
        print('Please report this error!')
        return

    print('Building PS2 CD image...\n')

    # TODO Iterate over tracks and build from that, instead of this fragile method
    with open(out_bin_fp, mode=f'{mode_bin}b') as io_bin:
        for i in range(0, len(iml_cd.loc.entries)):
            entry = iml_cd.loc.entries[i]

            print(f'Processing entry {i}...')

            if not os.path.exists(entry.source):
                print(f'File \"{entry.source}\" does not exist!')
                print('Aborting operation!')
                return

            io_bin.seek(entry.start * CD_SECTOR_SIZE, io.SEEK_SET)

            print(f'Reading file \"{entry.source}\"...')
            with open(entry.source, mode='rb+') as io_entry:
                if entry.mode == '2.1':  # CD-ROM XA Mode 2 Form 1
                    # write in blocks of 2352
                    read_data_block = io_entry.read(DVD_SECTOR_SIZE)  # read a "sector" of data
                    while len(read_data_block) != 0:
                        fucked_time = convert_to_time(io_bin.tell())

                        # sector sync
                        io_bin.write(CD_SYNC_PATTERN)

                        # header
                        # WTF is wrong with this system
                        io_bin.write(fucking_bullshit_conversion[fucked_time.minutes])
                        io_bin.write(fucking_bullshit_conversion[fucked_time.seconds])
                        io_bin.write(fucking_bullshit_conversion[fucked_time.fractions])
                        # breakpoint()
                        io_bin.write(b'\x02')  # mode - always 2

                        # subheader
                        io_bin.write(b'\x00' * 8)  # zeroed out?

                        # user data
                        if fucked_time.minutes == 0 and fucked_time.seconds == 2 and fucked_time.fractions == 14:  # disc info?
                            io_bin.write(iml_cd.cue.disc_name.encode(encoding='ascii'))
                            io_bin.write(iml_cd.cue.producer.encode(encoding='ascii'))
                            io_bin.write(iml_cd.cue.copyright.encode(encoding='ascii'))
                            io_bin.write(str(iml_cd.cue.creation_date).encode(encoding='ascii'))
                            io_bin.write(b'\x00' * 664)  # area for master disc..?

                            io_bin.write(b'\x20' * 48)  # 1280 byte area for... mastering comments??
                            io_bin.write(
                                'This bin file was built by iml2iso. https://github.com/master801/iml2iso'
                                .encode(encoding='ascii')
                            )
                            io_bin.write(b'\x20' * 1160)
                            pass
                        else:
                            io_bin.write(read_data_block)
                            pass
                        io_bin.seek(DVD_SECTOR_SIZE - len(read_data_block), io.SEEK_CUR)  # jump bytes for full 2048

                        # EDC (CRC32)
                        io_bin.seek(-(8 + DVD_SECTOR_SIZE), io.SEEK_CUR)  # subheader + user data
                        edc_data = io_bin.read(8 + DVD_SECTOR_SIZE)  # edc is calculated from subheader and user data
                        edc = fastcrc.crc32.cd_rom_edc(edc_data)
                        io_bin.write(struct.pack('<I', edc))

                        # ECC
                        # ecc parity p is calculated from header, subheader, user data and edc
                        peek1 = io_bin.tell()
                        io_bin.seek(-(4 + DVD_SECTOR_SIZE + 8 + 4), io.SEEK_CUR)
                        ecc_p_data = io_bin.read(4 + 8 + DVD_SECTOR_SIZE + 4)
                        # io_bin.seek(peek1, io.SEEK_SET)
                        io_bin.write(b'\x00' * 172)  # TODO Calculate and write ECC P

                        # ecc parity q is calculated from header, subheader, user data, edc and ecc parity p
                        peek2 = io_bin.tell()
                        io_bin.seek(-(172 + 4 + DVD_SECTOR_SIZE + 8 + 4), io.SEEK_CUR)
                        ecc_p_data = io_bin.read(4 + 8 + DVD_SECTOR_SIZE + 4 + 172)
                        # io_bin.seek(peek2, io.SEEK_SET)
                        io_bin.write(b'\x00' * 104)  # TODO Calculate and write ECC Q

                        read_data_block = io_entry.read(DVD_SECTOR_SIZE)
                        continue
                    pass
                else:
                    print(f'Unknown mode \"{entry.mode}\"!')
                    print('Please report this error!')
                    return
                print('Done\n')
                pass
            continue

        # write lead-out area
        # TODO This is specified by last CUE Track AA - make this less inflexible
        # lead_out_track = iml_cd.cue.tracks[-1]
        for i in range(0, 150):
            fucked_time = convert_to_time(io_bin.tell())

            io_bin.write(CD_SYNC_PATTERN)
            io_bin.write(fucking_bullshit_conversion[fucked_time.minutes])
            io_bin.write(fucking_bullshit_conversion[fucked_time.seconds])
            io_bin.write(fucking_bullshit_conversion[fucked_time.fractions])
            io_bin.write(b'\x02')  # mode
            io_bin.write(b'\x00' * (CD_SECTOR_SIZE - 0x10))
            continue
        pass
    del io_bin

    with open(out_cue_fp, f'{mode_cue}t', encoding='ascii') as io_cue:
        io_cue.write(f'FILE \"' + os.path.basename(out_bin_fp) + '\" BINARY\n')
        io_cue.write('  TRACK 01 MODE2/2352\n')
        io_cue.write('    INDEX 01 00:00:00\n')
        pass
    del io_cue
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
