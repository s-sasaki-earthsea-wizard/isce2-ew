import numpy as np
from osgeo import gdal
import os
import argparse

def create_geotiff(input_file, output_file, band=1):
    """
    Convert ISCE2 results to GeoTIFF
    
    Parameters:
    -----------
    input_file : str
        Input file path (vrt file)
    output_file : str
        Output GeoTIFF file path
    band : int
        Read band number (default: 1)
    """
    # Open input file
    ds = gdal.Open(input_file)
    if ds is None:
        raise ValueError(f"Failed to open file: {input_file}")
    
    # Read data
    data = ds.GetRasterBand(band).ReadAsArray()
    
    # Create output driver
    driver = gdal.GetDriverByName('GTiff')
    
    # Create output file
    out_ds = driver.Create(
        output_file,
        ds.RasterXSize,
        ds.RasterYSize,
        1,  # Number of bands
        gdal.GDT_Float32  # Data type
    )
    
    # Copy geometry information
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())
    
    # Write data
    out_ds.GetRasterBand(1).WriteArray(data)
    
    # Close file
    ds = None
    out_ds = None

def find_vrt_files(base_dir):
    """
    Find .vrt files in the specified directory
    
    Parameters:
    -----------
    base_dir : str
        Directory path to search
    
    Returns:
    --------
    dict : Dictionary of file types and paths
    """
    vrt_files = {}
    
    # Search .vrt files in the specified directory only
    for file in os.listdir(base_dir):
        if file.endswith('.vrt'):
            file_path = os.path.join(base_dir, file)
            print(f"Found .vrt file: {file_path}")
            
            # Find DEM .vrt file (wgs84 version)
            if file.endswith('dem.wgs84.vrt'):
                if 'dem' in vrt_files:
                    raise ValueError(f"❌ Multiple DEM files found. Using: {file_path}")
                vrt_files['dem'] = file_path
            
            # Find interferogram .vrt file (filtPhase.cor)
            elif file == 'filtPhase.cor.vrt':
                if 'interferogram' in vrt_files:
                    raise ValueError(f"❌ Multiple interferogram files found. Using: {file_path}")
                vrt_files['interferogram'] = file_path
    
    if not validate_vrt_files(vrt_files):
        raise ValueError("❌ Required .vrt files not found")
    
    return vrt_files

def validate_vrt_files(vrt_files):
    """
    Validate the presence of required .vrt files
    
    Parameters:
    -----------
    vrt_files : dict
        Dictionary of file types and paths
    
    Returns:
    --------
    bool
        True if all required files are present
    """
    required_files = {
        'dem': lambda f: f.endswith('dem.wgs84.vrt'),
        'interferogram': lambda f: f == 'filtPhase.cor.vrt'
    }
    
    for file_type, validator in required_files.items():
        if file_type not in vrt_files:
            raise ValueError(f"❌ {file_type.capitalize()} .vrt file not found")
        if not validator(os.path.basename(vrt_files[file_type])):
            raise ValueError(f"❌ Invalid {file_type} file: {vrt_files[file_type]}")
    
    return True

def parse_args():
    """
    Parse command line arguments
    
    Returns:
    --------
    argparse.Namespace
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Convert ISCE2 results to GeoTIFF')
    parser.add_argument('--input-dir', required=True, help='ISCE2 results directory')
    parser.add_argument('--output-dir', default='/app/visualize-outputs',
                       help='Output directory for GeoTIFF files')
    return parser.parse_args()

def generate_output_file_names(vrt_files, output_dir, input_dir):
    """
    Generate output file names
    
    Parameters:
    -----------
    vrt_files : dict
        Dictionary of file types and paths
    output_dir : str
        Base output directory path
    input_dir : str
        Input directory path
    
    Returns:
    --------
    dict
        Dictionary of output file names
    """
    # Get scene name from input directory
    scene_name = os.path.basename(input_dir)
    
    # Create scene-specific output directory
    scene_output_dir = os.path.join(output_dir, scene_name)
    scene_output_dir_name = os.path.basename(scene_output_dir)
    os.makedirs(scene_output_dir, exist_ok=True)
    
    # Generate output file names
    dem_output = os.path.join(scene_output_dir, f'{scene_output_dir_name}_dem.tif')
    interferogram_output = os.path.join(scene_output_dir, f'{scene_output_dir_name}_interferogram.tif')
    correlation_output = os.path.join(scene_output_dir, f'{scene_output_dir_name}_correlation.tif')

    return {
        'dem': dem_output,
        'interferogram': interferogram_output,
        'correlation': correlation_output
    }

def convert_files(vrt_files, output_files):
    """
    Convert all files to GeoTIFF format
    
    Parameters:
    -----------
    vrt_files : dict
        Dictionary of input file paths
    output_files : dict
        Dictionary of output file paths
    """
    # Convert DEM
    try:
        create_geotiff(vrt_files['dem'], output_files['dem'])
        print("✅ DEM conversion completed")
    except Exception as e:
        print(f"❌ Error occurred while converting DEM: {e}")
    
    # Convert interferogram
    try:
        create_geotiff(vrt_files['interferogram'], output_files['interferogram'])
        print("✅ Interferogram conversion completed")
    except Exception as e:
        print(f"❌ Error occurred while converting interferogram: {e}")
    
    # Convert correlation map
    try:
        create_geotiff(vrt_files['interferogram'], output_files['correlation'], band=2)
        print("✅ Correlation map conversion completed")
    except Exception as e:
        print(f"❌ Error occurred while converting correlation map: {e}")

def main():
    """
    Main function to convert ISCE2 results to GeoTIFF
    """
    args = parse_args()
    
    # Search .vrt files
    vrt_files = find_vrt_files(args.input_dir)
    
    # Generate output file names
    output_files = generate_output_file_names(vrt_files, args.output_dir, args.input_dir)
    
    # Convert files
    convert_files(vrt_files, output_files)

if __name__ == "__main__":
    main()