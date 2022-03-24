import iris
import xarray as xr
import pandas as pd
import numpy as np
import cartopy.crs as ccrs

def add_lat_lon(cube, inplace=False, geodetic=None):
    '''
    Calculate latitude and longitude from a cube and add as AuxCoords to that cube
    TODO:
     - Check that incoming cube doesn't already have lat and lon DimCoords
     - Check that incoming cube doesn't already have lat and lon AuxCoords
    '''
    if not inplace:
        cube = cube.copy()
    
    if geodetic==None:
        geodetic = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
    
    cube_crs = cube.coord_system().as_cartopy_crs()
    
    x = cube.coord(dim_coords=True, axis='X')
    y = cube.coord(dim_coords=True, axis='Y')

    mx, my = np.meshgrid(x.points, y.points)

    latlons = geodetic.as_cartopy_crs().transform_points(cube_crs, mx, my)

    lons = latlons[:,:,0]
    lats = latlons[:,:,1]

    lat_coord = iris.coords.AuxCoord(lats, 
                                     standard_name='latitude',
                                     long_name='latitude', 
                                     units='degrees',
                                     coord_system=geodetic)
    lon_coord = iris.coords.AuxCoord(lons, 
                                     standard_name='longitude',
                                     long_name='longitude', 
                                     units='degrees',
                                     coord_system=geodetic)

    cube.add_aux_coord(lat_coord, (y.cube_dims(cube)[0], x.cube_dims(cube)[0]))
    cube.add_aux_coord(lon_coord, (y.cube_dims(cube)[0], x.cube_dims(cube)[0]))
    
    return cube


def cube_to_dataframe(cube):
    '''
    Convert an Iris Cube to a wide Pandas dataframe via Xarray
    '''
    return (xr.DataArray.from_iris(cube)
            .to_dataframe()
            .reset_index()
            .drop_duplicates(ignore_index=True)
           )


if __name__=="__main__":
    print("Pandarris?")
    fname_eu = "pr_rcp85_land-rcm_eur_12km_01_day_20201201-20301130.nc"
    cube_to_dataframe(add_lat_lon(iris.load_cube(fname_eu))).head()