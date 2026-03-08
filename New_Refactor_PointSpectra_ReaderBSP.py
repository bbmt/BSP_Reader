#%%
import olefile
import os
import re
import struct
import numpy as np
import csv
#%%
filename = r"C:\Users\bruno\Documents\BSP_Reader\files_for_test\multi-spectral3.bsp"
path_to_save = 'files_for_test'
os.makedirs(path_to_save+'/Spectra',exist_ok=True)
os.makedirs(path_to_save+'/Interferogram',exist_ok=True)
os.makedirs(path_to_save+'/Images',exist_ok=True)
os.makedirs(path_to_save+'/TempBin',exist_ok=True)
#%%
if olefile.isOleFile(filename):
    with olefile.OleFileIO(filename) as ole:
        streams = ole.listdir(storages=False, streams=True)

        streams_list = ole.openstream(['Spectra','IndexTable']).read()
        
        streams_list = re.findall(rb'(\w{8}-\w{8})',streams_list)
        print("Found the following data. Showing internal ID")
        print(streams_list)

#  with olefile.OleFileIO(filename) as ole:
        stream_data = []
        for stream_ in streams_list:
            stream_data.append(ole.openstream(['Spectra',stream_.decode()]).read())

for name,data in zip(streams_list,stream_data):
    with open(path_to_save+'/TempBin/'+name.decode()+'.bin','wb+') as f:
        f.write(data)
# %%
for stream_name in streams_list:
    print("-"*60)
    print("-"*60)
    print(f'Data stream:{stream_name}')
    with open(path_to_save+'/TempBin/'+stream_name.decode()+'.bin', 'rb') as f:
        full_extracted_data = f.read()
        spectra_signature =  b'\x04\x00\x00\x00Data\x00\x00\x00\x00\x01' 
        d = {}

        idx = full_extracted_data.find(spectra_signature)+4
        if idx == -1:
            print("[ERROR] Data Signature not found.")
        else:  
            print(f'Data Signature found at:0x{idx:08X}' )

            # spectra_ptsep = 40:48  idx+32:idx+40
            # spectra_startpt = 52:56 idx+44:idx+48
            # spectra_npts = 60:64 idx+52:idx+56
            # Spectra_array_len_bytes = 64:68 idx+56:idx+60
            # init_data = 68 idx+60
    
            d['Spectra_PtSep'] = struct.unpack('<d',full_extracted_data[idx+32:idx+40])[0]
            d['Spectra_StartPt'] = struct.unpack('<I',full_extracted_data[idx+44:idx+48])[0]
            d['Spectra_Npts'] = struct.unpack('<I',full_extracted_data[idx+52:idx+56])[0]
            d['Spectra_Array_Len_Bytes'] = struct.unpack('<I',full_extracted_data[idx+56:idx+60])[0]

            print(f" -> Number of points for Spectrum: {d['Spectra_Npts']}")
            print(f" -> Array Lenght in Bytes: {d['Spectra_Array_Len_Bytes']} bytes")
            if d['Spectra_Npts']*8==d['Spectra_Array_Len_Bytes']:
                print('[Sanity Check]: Size of array is correct.')
            
                data_block = np.frombuffer(full_extracted_data[idx+60:d['Spectra_Array_Len_Bytes']+idx+60], dtype='<f8')

                d['Spectra'] = data_block

                wavenumber = [d['Spectra_PtSep'] * (d['Spectra_StartPt'] + i) for i in range(d['Spectra_Npts'])]
        
        print("\n")
        inteferogram_signature = b'\x0d\x00\x00\x00Interferogram\x00'

        idx2 = full_extracted_data.find(inteferogram_signature)+4
        if idx2 == -1:
            print("[ERROR] Interferogram Signature not found.")
        else:  
            print(f'Interferogram Signature found at:0x{idx2:08X}' )

            d['Inter_PtSep'] = struct.unpack('d',full_extracted_data[idx2+85:idx2+93])[0]
            d['Inter_StartPt'] = struct.unpack('i',full_extracted_data[idx2+97:idx2+101])[0]
            d['Inter_Npts'] = struct.unpack('i',full_extracted_data[idx2+105:idx2+109])[0]
            d['Inter_Array_Len_Bytes'] = struct.unpack('i',full_extracted_data[idx2+109:idx2+113])[0]

            print(f" -> Number of points for Interferogram: {d['Inter_Npts']}")
            print(f" -> Array Lenght in Bytes: {d['Inter_Array_Len_Bytes']} bytes")

            if d['Inter_Npts']*8==d['Inter_Array_Len_Bytes']:
                print('[Sanity Check]: Size of array is correct.')
            
                data_block = np.frombuffer(full_extracted_data[idx+60:d['Inter_Array_Len_Bytes']+idx+60], dtype='<f8')

                d['Interferogram'] = data_block

                optical_retardation = [d['Inter_PtSep'] * (d['Inter_StartPt'] + i) for i in range(d['Inter_Npts'])]
        print("\n")
    
    spectname_signature =b'\x09\x00\x00\x00SpectName'
    idx3 = full_extracted_data.find(spectname_signature)+4
    if idx3 == -1:
        print("[ERROR] SpectName Signature not found.")
    else:  
        print(f'SpectName Signature found at:0x{idx3:08X}' )
        idx_100 = full_extracted_data.find(b'1.00', idx3, idx3 + 100)
        pos = idx_100 + 4
        header = struct.unpack('<IIIII', full_extracted_data[pos:pos+20])
        prop_id, prop_type, _, size_a, size_b = header
        if prop_type == 2 and size_a == size_b:
            string_start = pos + 20
            string_end = string_start + size_a
            
            # We slice the byte array exactly by the declared size
            name_bytes = full_extracted_data[string_start : string_end]
            sample_name = name_bytes.decode('ascii', errors='ignore')
            
            # Handle empty strings gracefully
            if not sample_name:
                sample_name = "[NO_SAMPLE_NAME]"
            else:
                sample_name = sample_name

            print(f"SpectName found at offset 0x{idx3:08X}: {sample_name}")
        else:
            print(f"Warning: Unexpected structure after SpectName at offset {idx3:08X}")
    
    print('Saving Spectra...')
    with open(path_to_save+'/Spectra/'+stream_name.decode()+'_'+sample_name+'_spectrum.csv', 'w+') as csv_file:
        writer = csv.writer(csv_file,dialect='excel')
        writer.writerow(['Wavenumber (cm-1)','Values'])
        writer.writerows(zip(wavenumber,d['Spectra']))
    
    print('Saving Interferogram...')
    with open(path_to_save+'/Interferogram/'+stream_name.decode()+'_'+sample_name+'_interferogram.csv', 'w+') as csv_file:
        writer = csv.writer(csv_file,dialect='excel')
        writer.writerow(['Optical Retardation','Signal (Volts)'])
        writer.writerows(zip(optical_retardation,d['Interferogram']))
    print("====================")
    print("= Extracting Image =")
    print("====================")

    jpg_byte_start = b'\xff\xd8\xff\xe0'
    jpg_byte_end = b'\xff\xd9'
    jpg_image = bytearray()

    start_img = full_extracted_data.find(jpg_byte_start)
    if start_img == -1:
        print('!Warning!Could not find a valid JPEG image in the data stream:'+stream_name.decode())
        print('This is ok if you did not take a visible image for this spectrum'+'\n')
    else:
        print(f'Image found:{stream_name.decode()}_{sample_name}\n Saving image...')
        end_img = full_extracted_data.find(jpg_byte_end, start_img) + len(jpg_byte_end)
        jpg_image += full_extracted_data[start_img:end_img]
        with open(path_to_save+'/Images/'+stream_name.decode()+'_'+sample_name+'.jpg', 'wb+') as f:
            f.write(jpg_image)
    print("-"*60)
    print("-"*60)

# %%
