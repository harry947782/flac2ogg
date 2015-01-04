#!/usr/bin/env python3
from os.path import os
from multiprocessing.pool import Pool
import subprocess
from subprocess import DEVNULL
import argparse

def isFlacFile(filename):
    return 'flac' == str(os.path.splitext(filename)[1][1:]).lower();

def findFiles(directory):
    for root, _, files in os.walk(directory):
        for f in files:
            yield os.path.relpath(os.path.join(root, f), directory)

def findFlacFiles(directory):
    return filter(isFlacFile, findFiles(directory))

def oggFilename(outputdir, flacFilename):
    return os.path.join(outputdir, os.path.splitext(flacFilename)[0] + '.ogg')

def createConvertPairs(inputDirectory, outputDirectory, flacFiles):
    for file in flacFiles:
        yield os.path.join(inputDirectory, file), oggFilename(outputDirectory, file)

def oggFileExists(convertPair):
    _, outfile = convertPair
    return os.path.exists(outfile)

def filesNeedingConverting(inputDirectory, outputDirectory):
    return filter(lambda x : not oggFileExists(x), createConvertPairs(inputDirectory, outputDirectory, findFlacFiles(inputDirectory)))

def convertFile(convertPair):
    infile, outfile = convertPair
    print("converting file: ", infile, " into ", outfile)
    subprocess.call(['oggenc', '-q6', infile, '-o', outfile], stderr=DEVNULL, stdout=DEVNULL);

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Duplicate a directory structure of flac files into ogg files.')
    parser.add_argument('inputDirectory', metavar='indir', type=str, help='The directory to look for flac files')
    parser.add_argument('outputDirectory', metavar='outdir', type=str, help='The directory to put the ogg files')
    args = parser.parse_args();
    processPool = Pool(5)
    processPool.map(convertFile, filesNeedingConverting(args.inputDirectory, args.outputDirectory))
