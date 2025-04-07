import matplotlib.pyplot as plt
import numpy as np
import rasterio
import os
from pathlib import Path
from rasterio.transform import from_origin


def plot_complex_data(
    raster_filename: str,
    output_filename: str,
    dem_file: str = None,
    title: str = None,
    aspect: int = 1,
    datamin: int = None,
    datamax: int = None,
    interpolation: str = "nearest",
    draw_colorbar: bool = False,
    colorbar_orientation: str = "horizontal",
) -> None:
    # Load the data using rasterio
    with rasterio.open(raster_filename) as src:
        # Read data
        data = src.read(1)  # Read first band
        
        # Get transform and bounds
        transform = src.transform
        bounds = src.bounds
        crs = src.crs
        
        # Check if geospatial information is missing
        if transform.is_identity and dem_file:
            print("Warning: Input file has no geospatial information. Using DEM file as reference.")
            with rasterio.open(dem_file) as dem:
                transform = dem.transform
                bounds = dem.bounds
                crs = dem.crs
        
        # Get extent
        xmin = bounds.left
        xmax = bounds.right
        ymin = bounds.bottom
        ymax = bounds.top

    # Put all zero values to nan and do not plot nan
    try:
        data[data == 0] = np.nan
    except:
        pass

    # Create figure for visualization
    fig = plt.figure(figsize=(18, 16))
    
    # Plot amplitude
    ax = fig.add_subplot(1, 2, 1)
    cax1 = ax.imshow(
        np.abs(data),
        vmin=datamin,
        vmax=datamax,
        cmap="gray",
        extent=[xmin, xmax, ymin, ymax],
        interpolation=interpolation,
    )
    ax.set_title(title + " (amplitude)")
    if draw_colorbar:
        _ = fig.colorbar(cax1, orientation=colorbar_orientation)
    ax.set_aspect(aspect)

    # Plot phase
    ax = fig.add_subplot(1, 2, 2)
    cax2 = ax.imshow(
        np.angle(data),
        cmap="rainbow",
        vmin=-np.pi,
        vmax=np.pi,
        extent=[xmin, xmax, ymin, ymax],
        interpolation=interpolation,
    )
    ax.set_title(title + " (phase [rad])")
    if draw_colorbar:
        _ = fig.colorbar(cax2, orientation=colorbar_orientation)
    ax.set_aspect(aspect)

    # Save figure as PNG for quick viewing
    png_filename = output_filename.replace('.tif', '.png')
    plt.savefig(png_filename)
    plt.close()

    # Save visualization as GeoTIFF
    amplitude = np.abs(data)
    phase = np.angle(data)
    
    # Create a 3-band GeoTIFF (amplitude, phase, and a mask)
    with rasterio.open(
        output_filename,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=3,
        dtype=amplitude.dtype,
        crs=crs if crs else rasterio.CRS.from_epsg(4326),  # Use DEM's CRS or WGS84
        transform=transform,
    ) as dst:
        # Write amplitude to band 1
        dst.write(amplitude, 1)
        
        # Write phase to band 2
        dst.write(phase, 2)
        
        # Write mask to band 3 (1 for valid data, 0 for NaN)
        mask = ~np.isnan(amplitude)
        dst.write(mask.astype(np.uint8), 3)
        
        # Set band descriptions
        dst.set_band_description(1, "Amplitude")
        dst.set_band_description(2, "Phase [rad]")
        dst.set_band_description(3, "Valid data mask")

    # Clear the data
    data = None


if __name__ == "__main__":
    input_dir = "/app/results/Noto_20230606-20240102_2830/interferogram/"
    print(input_dir)

    # Get the output directory from environment variable or use default
    output_dir = os.getenv("OUTPUT_DIR", "/app/visualize-outputs")
    output_dir = Path(output_dir)
    print(output_dir)

    # Get DEM file path
    dem_file = os.path.join("/app/results/Noto_20230606-20240102_2830", "demLat_N36_N38_Lon_E136_E137.dem.wgs84.vrt")
    print(f"Using DEM file: {dem_file}")

    plot_complex_data(
        raster_filename=os.path.join(input_dir, "filt_topophase.flat.vrt"),
        output_filename=str((output_dir / "filt_topophase.flat.tif").resolve()),
        dem_file=dem_file,
        title="MERGED FILT IFG ",
        aspect=1,
        datamin=0,
        datamax=10000,
        draw_colorbar=True,
    ) 