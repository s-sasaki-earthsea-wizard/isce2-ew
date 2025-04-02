import numpy as np
import rasterio
import os
import argparse

def create_geotiff(input_file, output_file, dem_file_path=None, band=1):
    """
    Convert ISCE2 results to GeoTIFF
    
    Parameters:
    -----------
    input_file : str
        Input file path (vrt file)
    output_file : str
        Output GeoTIFF file path
    dem_file_path : str, optional
        DEM file path to get geotransform information
    band : int
        Read band number (default: 1)
    """
    # Open input file
    with rasterio.open(input_file) as src:
        # Read data
        data = src.read(band)
        
        # Get metadata
        meta = src.meta.copy()
        
        # If dem_file is provided and input is not DEM, use DEM's geotransform
        if dem_file_path and 'dem' not in input_file:
            with rasterio.open(dem_file_path) as dem:
                meta.update({
                    'count': 1,  # Number of bands
                    'dtype': 'float32',
                    'driver': 'GTiff',
                    'crs': dem.crs,
                    'transform': dem.transform
                })
        else:
            meta.update({
                'count': 1,  # Number of bands
                'dtype': 'float32',
                'driver': 'GTiff',
                'crs': src.crs,
                'transform': src.transform
            })
        
        # Create output file
        with rasterio.open(output_file, 'w', **meta) as dst:
            dst.write(data, 1)

def find_dem_file(base_dir: str) -> str:
    """
    Find DEM file in the specified directory

    Args:
        base_dir (str): The base directory to search for DEM files

    Returns:
        str: The path to the DEM file
    """
    # List all files in the directory
    for file in os.listdir(base_dir):
        if file.endswith('dem.wgs84.vrt'):
            dem_file_path = os.path.join(base_dir, file)
            print(f"✅🔍 Found WGS84 DEM file: {dem_file_path}")
            return dem_file_path
    
    # If no file is found, raise error
    raise ValueError(f"❌ Required WGS84 DEM file not found in: {base_dir}")

def find_interferogram_file(base_dir: str) -> str:
    """
    Find interferogram file in the specified directory

    Args:
        base_dir (str): The base directory to search for interferogram files

    Returns:
        str: The path to the interferogram file
    """
    interferogram_dir = os.path.join(base_dir, 'interferogram')
    if not os.path.isdir(interferogram_dir):
        raise ValueError(f"⚠️ Interferogram directory not found at: {interferogram_dir}")

    unw_file = os.path.join(interferogram_dir, 'filt_topophase.unw.vrt')
    if os.path.exists(unw_file):
        print(f"✅🔍 Found unwrapped interferogram file: {unw_file}")
        return unw_file
    else:
        raise ValueError(f"❌ Required unwrapped interferogram file not found: {unw_file}")

def add_dem_and_interferogram_to_vrt(base_dir: str) -> dict:
    """
    Add DEM and interferogram files to the VRT files dictionary

    Args:
        base_dir (str): The base directory to search for files

    Returns:
        dict: Dictionary containing file paths
    """
    vrt_files = {}
    
    # Find and add DEM file
    vrt_files['dem'] = find_dem_file(base_dir)
    
    # Find and add interferogram file
    vrt_files['interferogram'] = find_interferogram_file(base_dir)
    
    return vrt_files

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
    vrt_files = add_dem_and_interferogram_to_vrt(base_dir)
    
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
        'interferogram': lambda f: f == 'filt_topophase.unw.vrt'
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
    os.makedirs(scene_output_dir, exist_ok=True)
    
    # Generate output file names with scene name prefix
    dem_output = os.path.join(scene_output_dir, f'{scene_name}_dem.tif')
    interferogram_output = os.path.join(scene_output_dir, f'{scene_name}_interferogram.tif')
    correlation_output = os.path.join(scene_output_dir, f'{scene_name}_correlation.tif')

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
        create_geotiff(vrt_files['dem'], output_files['dem'], dem_file_path=vrt_files['dem'])
        print("✅ DEM conversion completed")
    except Exception as e:
        print(f"❌ Error occurred while converting DEM: {e}")
    
    # Convert interferogram
    try:
        create_geotiff(vrt_files['interferogram'], output_files['interferogram'], dem_file_path=vrt_files['dem'])
        print("✅ Interferogram conversion completed")
    except Exception as e:
        print(f"❌ Error occurred while converting interferogram: {e}")
    
    # Convert correlation map
    try:
        create_geotiff(vrt_files['interferogram'], output_files['correlation'], dem_file_path=vrt_files['dem'], band=2)
        print("✅ Correlation map conversion completed")
    except Exception as e:
        print(f"❌ Error occurred while converting correlation map: {e}")

def main():
    """
    Main function to convert ISCE2 results to GeoTIFF
    """
    args = parse_args()
    
    # Ensure input_dir is an absolute path
    input_dir = os.path.abspath(args.input_dir)
    print(f"🔍 Processing directory: {input_dir}")
    
    # Search .vrt files
    vrt_files = find_vrt_files(input_dir)
    
    # Generate output file names
    output_files = generate_output_file_names(vrt_files, args.output_dir, input_dir)
    
    # Print output file paths for debugging
    print("\n📁 Output files will be created at:")
    for file_type, path in output_files.items():
        print(f"  - {path}")
    
    # Convert files
    convert_files(vrt_files, output_files)

if __name__ == "__main__":
    main()