from flask import request

import pyard
from pyard.blender import DRBXBlenderError
from pyard.exceptions import PyArdError, InvalidAlleleError

# Globally accessible for all endpoints
print("py-ard version: ", pyard.__version__)
ard = pyard.init()
print("IMGT version:   ", ard.get_db_version())


def validate_controller():
    if request.json:
        # Check the request has required inputs
        try:
            gl_string = request.json["gl_string"]
        except KeyError:
            return {"message": "gl_string not provided"}, 404
        # Validate
        try:
            ard.validate(gl_string)
            return {"valid": True}, 200
        except InvalidAlleleError as e:
            return {
                "valid": False,
                "message": f"Provided GL String is invalid: {gl_string}",
                "cause": e.message,
            }, 404
        except PyArdError as e:
            return {"message": e.message}, 400


def redux_controller():
    if request.json:
        # Check the request has required inputs
        try:
            gl_string = request.json["gl_string"]
            reduction_method = request.json["reduction_method"]
        except KeyError:
            return {"message": "gl_string and reduction_method not provided"}, 404
        # Perform redux
        try:
            redux_string = ard.redux(gl_string, reduction_method)
            return {"ard": redux_string}, 200
        except PyArdError as e:
            return {"message": e.message}, 400

    # if no data is sent
    return {"message": "No input data provided"}, 404


def mac_expand_controller(allele_code: str):
    try:
        if ard.is_mac(allele_code):
            alleles = ard.expand_mac(allele_code)
            return {
                "mac": allele_code,
                "alleles": alleles,
                "gl_string": "/".join(alleles),
            }, 200
        else:
            return {"message": f"{allele_code} is not a valid MAC"}, 404
    except PyArdError as e:
        return {"message": e.message}, 400


def drbx_blender_controller():
    if request.json:
        try:
            drb1_slug = request.json["DRB1_SLUG"]
            drb3 = request.json["DRB3"]
            drb4 = request.json["DRB4"]
            drb5 = request.json["DRB5"]
        except KeyError:
            return {"message", "All of DRB1_SLUG, DRB3, DRB4, DRB5 values not provided"}

        try:
            blended_drbx = pyard.dr_blender(drb1_slug, drb3, drb4, drb5)
            return {"DRBX_blend": blended_drbx}
        except DRBXBlenderError as e:
            return {"found": e.found, "expected": e.expected}


def version_controller():
    version = ard.get_db_version()
    return {"version": version}, 200


def splits_controller(allele: str):
    mapping = pyard.find_broad_splits(allele)
    if mapping:
        return {"broad": mapping[0], "splits": mapping[1]}, 200

    return {"message": f"No Broad/Splits matched {allele}"}, 404
