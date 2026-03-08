# A Reader for Agilent BSP files

The BSP files of Agilent IR spectrometer is a OLE2 Microsoft format.
The reader depends on the olefile package for extracting the binary stream inside the location [SPECTRA, ID], where ID is a alphanumeric string given for each spectra by the Agilent Resolution software.

Moreover, inside the binary stream the data seems to be packaged as TLV, Type-Lenght-Value, this is useful to check if data extraction is correct. This pattern does not to fit all the stream, sometime there are variants. 

# For Users

Please use the links bellow. It will redirect to Google Colab. Please follow the instruction there.

- [FPA - To extract image from FPA files](https://colab.research.google.com/github/bbmt/BSP_Reader/blob/main/FPA_ReaderBSP.ipynb)

- [Point Spectra - To extract spectra and images from BSP files](https://colab.research.google.com/github/bbmt/BSP_Reader/blob/main/New_Refactor_PointSpectra_ReaderBSP.ipynb)


### Updates
2026.03.08 - Refactored the code for PointSpectraReader. User had problems extracting data.

### TODO
- Pack everthing for easy install and maintenance
- Define functions and classes instead of a script.
- Allow multiple file processing for point spectra.