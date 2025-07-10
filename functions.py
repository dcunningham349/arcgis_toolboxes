def treecanopy(filename, tiles, junk_folder, coords):
    #import packages for function
    import os
    import requests
    import arcpy
    import tempfile as tf
    arcpy.env.overwriteOutput = True

    junk_path = tf.mkdtemp(dir= junk_folder, prefix = f"{filename}")

    url = tiles.loc[filename, 'aws_url']

    path = junk_path + '\\' + os.path.basename(url)
    response = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    arcpy.env.addOutputsToMap = False
    arcpy.conversion.ConvertLas(in_las=path, target_folder=junk_path,
                                define_coordinate_system="ALL_FILES", in_coordinate_system=coords)

    arcpy.AddMessage(f'Done downloading and converting {filename}')

    for file in os.listdir(junk_path):
        if filename in file and '.las' == file[-4:]:
            DSM_outpath = junk_path + '\\' + f"{filename}_DSM"
            arcpy.conversion.LasDatasetToRaster(in_las_dataset=junk_path + '\\' + file, out_raster=DSM_outpath,
                                                interpolation_type="BINNING MAXIMUM LINEAR")
            DSM = arcpy.Raster(DSM_outpath)

            # creating DTM
            DTM_outpath = junk_path + '\\' + f"{filename}_DTM"
            arcpy.conversion.LasDatasetToRaster(in_las_dataset=junk_path + '\\' + file, out_raster=DTM_outpath,
                                                interpolation_type="BINNING MINIMUM LINEAR")
            DTM = arcpy.Raster(DTM_outpath)

            calc = DSM - DTM
            treeCan_OP = junk_path + '\\' + f'{filename}_TC'
            calc.save(treeCan_OP)

            arcpy.management.Delete(DSM)
            arcpy.management.Delete(DTM)

    return f'Complete TreeCanopy for {filename}'

def dem_download(filename, tiles, junk_folder):
    #import packages for function
    import os
    import requests
    import arcpy
    import tempfile as tf
    arcpy.env.overwriteOutput = True

    junk_path = tf.mkdtemp(dir= junk_folder, prefix = f"{filename}")

    url = tiles.loc[filename, 'aws_url']

    path = junk_path + '\\' + os.path.basename(url)
    response = requests.get(url, stream=True)
    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return f'Complete DEM Download for {filename}'