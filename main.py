#!/usr/bin/env python3
# Created by Master on 3/16/2024

import argparse

import iml
import cd
import dvd


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
        dvd.convert_to_dvd_media(iml_data, iml_dual_layer, args.out_disc_image)
        pass
    elif iml_data.sys.media == 'CD':
        if iml_dual_layer != None:
            print('Dual layer iml was inputted, but CDs do not have a dual layer!')
            print('Exiting...')
            return
        cd.convert_to_cd_media(iml_data, args.out_disc_image)
        return
    else:
        print(f'Invalid media \"{iml_data.sys.media}\"!')
        return
    return


if __name__ == '__main__':
    main()
    pass
