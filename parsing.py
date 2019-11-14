"""Parsing code for DICOMS and contour files"""

import pydicom
from pydicom.errors import InvalidDicomError
import pandas as pd

import numpy as np
from PIL import Image, ImageDraw
import os
from flask import Flask

path = '/media/tan/8124db8a-fb2a-45fd-843b-88777c579f0e/tanushri/pycharm/arterys/final_data'

def parse_contour_file(filenames):
    """Parse the given contour filename

    :param filename: filepath to the contourfile to parse
    :return: list of tuples holding x, y coordinates of the contour
    """

    coords_lst = []
    ori_cont = df['original_id'].to_list()
    for ori in ori_cont:
        newpath = path + '/' + filenames[1] + '/' + ori + '/i-contours/'
        list_files = os.listdir(newpath)
        for filename in list_files:
            with open(filename, 'r') as infile:
                for line in infile:
                    coords = line.strip().split()

                    x_coord = float(coords[0])
                    y_coord = float(coords[1])
                    coords_lst.append((x_coord, y_coord))

    return coords_lst


def parse_dicom_file(filename):
    """Parse the given DICOM filename

    :param filename: filepath to the DICOM file to parse
    :return: dictionary with DICOM image data
    """
    patient_cont = df['patient_id'].to_list()
    for pat in patient_cont:
        newpath = path + '/' + filenames[0] + '/' + pat
        list_files = os.listdir(newpath)
        for file in list_files:
            try:
                dcm = pydicom.read_file(filename)
                dcm_image = dcm.pixel_array

            try:
                intercept = dcm.RescaleIntercept
            except AttributeError:
                intercept = 0.0
            try:
                slope = dcm.RescaleSlope
            except AttributeError:
                slope = 0.0

            if intercept != 0.0 and slope != 0.0:
                dcm_image = dcm_image*slope + intercept
                dcm_dict = {'pixel_data' : dcm_image}
                return dcm_dict

            except InvalidDicomError:
                    return None


def poly_to_mask(polygon, width, height):
    """Convert polygon to mask

    :param polygon: list of pairs of x, y coords [(x1, y1), (x2, y2), ...]
     in units of pixels
    :param width: scalar image width
    :param height: scalar image height
    :return: Boolean mask of shape (height, width)
    """

    # http://stackoverflow.com/a/3732128/1410871
    img = Image.new(mode='L', size=(width, height), color=0)
    ImageDraw.Draw(img).polygon(xy=polygon, outline=0, fill=1)
    mask = np.array(img).astype(bool)
    return mask

#### Get the list of files and folders and pass them to the following methods
@app.route("/")
def main():
    filenames = os.listdir(path)
    df = pd.read_csv(path + '/' + filenames[2])
    parse_contour_file(filenames)
    parse_dicom_file(filenames)


if __name__ == "__main__":
    app = Flask(__name__)
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
