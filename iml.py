#!/usr/bin/env python3
# Created by Master on 3/16/2024

import dataclasses
import os


@dataclasses.dataclass
class IML:

    @dataclasses.dataclass
    class Sys:

        version: str
        media: str  # should only be "DVD" or "CD"
        target: str  # accept only "PS2" - idk if PS1 is valid
        disc_version: str  # just leave this as a string...
        date: str  # year/month/day-hour-minute-second

        def __init__(self):
            return

        @staticmethod
        def parse(tag_list: list[str]):
            data_sys = IML.Sys()
            for tag in tag_list:
                stripped = tag.strip().split('=', maxsplit=1)
                key = stripped[0]
                value = stripped[1]

                if key == 'VERSION':
                    data_sys.version = value
                    pass
                elif key == 'MEDIA':
                    data_sys.media = value
                    if data_sys.media != 'DVD' and data_sys.media != 'CD':
                        print(f'Invalid media \"{data_sys.media}\"!')
                        return None
                    pass
                elif key == 'TARGET':
                    data_sys.target = value
                    if data_sys.target != 'PS2':
                        print('Target is other than \"PS2\"!')
                        return None
                    pass
                elif key == 'DISCVERSION':
                    data_sys.disc_version = value
                    pass
                elif key == 'DATE':
                    data_sys.date = value
                    pass
                else:
                    print('Something bad happened while parsing \"Sys\"!')
                    pass

                del value
                del key
                del stripped
                continue
            del tag
            return data_sys

    @dataclasses.dataclass
    class Cue:

        disc_name: str  # 32 byte string
        producer: str  # 32 byte string
        copyright: str  # 32 byte string
        creation_date: int  # yearmonthday
        ps_type: int
        disc_code: str  # padnumber (01)

        def __init__(self):
            return

        @staticmethod
        def parse(tag_list: list[str]):
            data_cue = IML.Cue()
            for tag in tag_list:
                stripped = tag.strip().split('=', maxsplit=1)
                key = stripped[0]
                value = stripped[1]

                if key == 'DISCNAME':
                    data_cue.disc_name = value.strip('\"')
                    if len(data_cue.disc_name) != 32:
                        print('Key \"DISCNAME\" is not 32 chars!')
                        return None
                    pass
                elif key == 'PRODUCER':
                    data_cue.producer = value.strip('\"')
                    if len(data_cue.producer) != 32:
                        print('Key \"PRODUCER\" is not 32 chars!')
                        return None
                    pass
                elif key == 'COPYRIGHT':
                    data_cue.copyright = value.strip('\"')
                    if len(data_cue.copyright) != 32:
                        print('Key \"COPYRIGHT\" is not 32 chars!')
                        return None
                    pass
                elif key == 'CREATIONDATE':
                    data_cue.creation_date = int(value)
                    pass
                elif key == 'PSTYPE':
                    data_cue.ps_type = int(value)
                    if data_cue.ps_type != 2:
                        print(f'Expected \"PSTYPE\" to be \"2\" but got \"{data_cue.ps_type}\"!')
                        return None
                    pass
                elif key == 'DISCCODE':
                    data_cue.disc_code = int(value)
                    pass
                else:
                    print('Something bad happened while parsing \"Cue\"!')
                    pass

                del value
                del key
                del stripped
                continue
            del tag
            return data_cue

    @dataclasses.dataclass
    class Loc:

        @dataclasses.dataclass
        class Entry:

            start: int
            end: int
            mode: str
            f_no: int  # ???
            source: str  # file path
            source_offset: int = None  # present if an offset is used

        entries: list[Entry]

        # noinspection PyComparisonWithNone
        @staticmethod
        def parse(tag_list: list[str]):
            entries: list[IML.Loc.Entry] = list()
            for tag in tag_list:
                data = tag.split(maxsplit=4)  # janky split
                entry: IML.Loc.Entry = None
                if len(data) == 5:
                    fp = data[4].split('\"')[1:]
                    if len(fp[1]) > 0:
                        entry = IML.Loc.Entry(int(data[0]), int(data[1]), data[2], int(data[3]), fp[0], int(fp[1]))
                        pass
                    else:
                        entry = IML.Loc.Entry(int(data[0]), int(data[1]), data[2], int(data[3]), fp[0])
                        pass
                    pass
                else:
                    print('Bad loc entry?!')
                    pass

                if entry != None:
                    entries.append(entry)
                    pass
                del entry
                del data
                continue
            del tag
            return IML.Loc(entries)

    sys: Sys
    cue: Cue
    loc: Loc

    # noinspection PyComparisonWithNone
    @staticmethod
    def parse_iml(fp_iml: str):
        if os.path.exists(fp_iml):
            if not os.path.isfile(fp_iml):
                print(f'Input \"{fp_iml}\" is not a file!?')
                return None
            pass
        else:
            print(f'Input \"{fp_iml}\" does not exist!')
            return None

        with open(fp_iml, mode='rt+', encoding='ascii') as io_iml:
            iml_file = io_iml.read().splitlines(keepends=False)
            pass

        if iml_file != None:
            has_tag = False
            tag_list: list[str] = list()

            print(f'Parsing IML file \"{fp_iml}\"...')

            data_sys: IML.Sys = None
            data_cue: IML.Cue = None
            data_loc: IML.Loc = None
            for i in range(0, len(iml_file)):
                line = iml_file[i].strip()
                if line.startswith('#'):  # ignore comments
                    print(f'Ignoring comment on line {i}...')
                    continue
                elif len(line) == 0:  # empty
                    continue

                if line.startswith('[') and not line[1] == '/' and line.endswith(']'):
                    has_tag = True
                    continue

                if has_tag:
                    if line.startswith('[/') and line.endswith(']'):
                        tag = line[2:-1]
                        if tag == 'SYS':
                            data_sys = IML.Sys.parse(tag_list.copy())
                            pass
                        elif tag == 'CUE':
                            data_cue = IML.Cue.parse(tag_list.copy())
                            pass
                        elif tag == 'LOC':
                            data_loc = IML.Loc.parse(tag_list.copy())
                            pass
                        else:
                            print(f'Unexpected tag \"{tag}\"!')
                            pass
                        has_tag = False  # reset state
                        tag_list.clear()
                        continue
                    tag_list.append(line)
                    pass
                continue
            del line
            del i

            if data_sys == None:
                print('Failed to parse \"SYS\"!')
                return None
            if data_cue == None:
                print('Failed to parse \"CUE\"!')
                return None
            if data_loc == None:
                print('Failed to parse \"LOC\"!')
                return None

            print(f'Found {len(data_loc.entries)} file entries')
            print('Done parsing IML file\n')
            return IML(data_sys, data_cue, data_loc)
        return None
