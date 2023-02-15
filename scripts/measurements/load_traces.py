import h5py  # Add support for hdf5 files
import numpy as np  # Add support for matrix manipulations

# path of the traces hdf5 file which will be used in the dpa analysis
traces_path = './traces.h5'


class load_traces:
    """Class used to load traces measured with measuring script."""

    def __init__(self, traces_path=traces_path):
        self.hdf5_file = h5py.File(traces_path, "r")

    def get_traces(self):
        """Returns measured traces in a matrix: trace-number x trace-length"""
        traces = self.hdf5_file["traces"][:].astype(np.int16)
        return traces

    def get_ciphertexts(self):
        """Returns ciphertexts in a matrix: trace-number x 16 bytes ciphertext"""
        ciphertexts = self.hdf5_file["ciphertext"][:].astype(np.uint8)
        return ciphertexts

    def get_plaintexts(self):
        """Returns plaintexts in a matrix: trace-number x 16 bytes plaintext"""
        plaintexts = self.hdf5_file["plaintext"][:].astype(np.uint8)
        return plaintexts
