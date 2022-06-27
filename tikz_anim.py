#!/usr/bin/env python3

import argparse
import numpy as np
from tqdm import tqdm
from pathlib import Path
from subprocess import run, DEVNULL

# CLI arguments
parser = argparse.ArgumentParser(description='Create TikZ animations')
parser.add_argument('-t', '--tex-file', default='', help='input TeX file')
parser.add_argument('-c', '--tex-engine', default='pdflatex', help='(La)TeX engine')
parser.add_argument('-v', '--variable-name', default='a', help='name for animated variable')
parser.add_argument('-s', '--start-value', type=float, default=0.0, help='start value for animated variable')
parser.add_argument('-e', '--end-value', type=float, default=9.0, help='end value for animated variable')
parser.add_argument('-j', '--step-value', type=float, default=1.0, help='step value for animated variable')
parser.add_argument('-i', '--convert-args', default='-quality 100 -density 300 -resize 700x700 -background white -alpha remove -alpha off', help='arguments for convert')
# parser.add_argument('-f', '--ffmpeg-args', default='-i %05d.png', help='arguments for ffmpeg')
parser.add_argument('-o', '--output-file-name', default='animation.mp4', help='output animation filename')
args = parser.parse_args()


# Some variables
var_values = np.arange(args.start_value, args.end_value+args.step_value, args.step_value)
frame_indices = [x for x in range(len(var_values))]
num_frames = len(frame_indices)
tex_file_path = Path(args.tex_file)
pdf_file_name = tex_file_path.stem + '.pdf'
animation_file_path = Path(args.output_file_name)
png_file_names = tex_file_path.stem + '_frame_' + '%05d' + '.png'


# Error handeling
errors = []

if num_frames < 0:
    errors.append('End value must be greater than or equal to start value.')

if not tex_file_path.is_file():
    errors.append(f'TeX file {str(tex_file_path)} not found.')

if len(errors) > 0:
    for error in errors:
        print(error)
    print('Exiting.')
    exit()

# Prepare commands
tex_cmd = lambda x: f'{args.tex_engine} -shell-escape "\def\{args.variable_name}{{{x:0.3f}}} \input{{{str(tex_file_path)}}}"'
png_name = lambda n: tex_file_path.stem + f'_frame_{n:05d}.png'
convert_cmd = lambda frame, png_filename: f'convert {args.convert_args} {pdf_file_name} {png_filename}'
ffmpeg_cmd = f'yes | ffmpeg -i {png_file_names} -vf "fps=120,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 {args.output_file_name}'

# Process animation
print(f'Animation length: {num_frames} frames.')
print('Creating frames')
for frame, val in enumerate(tqdm(var_values)):
    run(tex_cmd(val), stdout=DEVNULL, shell=True)
    p = png_name(frame)
    run(convert_cmd(frame, p), stdout=DEVNULL, shell=True)

print(f'Finished creating {num_frames} frames, converting to animation')
run(ffmpeg_cmd, stdout=DEVNULL, shell=True)
print('Done.')
