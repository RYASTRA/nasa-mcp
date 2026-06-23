# Vesta/Moon/Mars Trek WMTS

> **In plain terms:** Serves the map-tile imagery behind NASA's Mars, Moon, and Vesta "Trek" exploration portals. Access the mosaics through standard WMTS tile requests in your own mapping client to build interactive maps of other worlds.

Here we have the collection of APIs that power the awesome Mars Trek and Vesta Trek NASA web-based portals for exploration and have newly added Moon Trek. These APIs can be leveraged using your favorite OGC RESTFul Web Map and Tile Service (WMTS) client. Please visit [http://www.opengeospatial.org/standards/wmts](http://www.opengeospatial.org/standards/wmts) for more information about WMTS. To help you get started, we've included some demos using the ESRI javascript client library for Mars and Vesta.

This API is maintained and provided by the NASA Solar System Exploration Research Virtual Institute (SSERVI) and the Jet Propulsion Lab (JPL) Trek team.

## Available Moon Mosaics

Here is basic information about how to request image tiles from a RESTful WMTS service. The basic URL template is as follows:

```
http://{WMTS endpoint}/1.0.0/{Style}/{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}.png
```

\* Some services are .png and some are .jpg. Please look at WMTS GetCapabilities ResourcesURL element to find out what extension to use. In order to fill in the variables in the template URL, you need to parse the WMTS GetCapabilities XML. GetCapabilities XML can be found for each product below. From the WMTS GetCapabilities XML, find ows:Identifier element inside Style element. This value replaces {Style}. The ows:Identifier element inside TileMatrixSet element replaces {TileMatrixSet}. Inside the TileMatrixSet element in WMTS Capabilities, there is a list of TileMatrix. This is the Zoom level. Replace {TileMatrix} with the ows:Identifier found in TileMatrix element. {TileRow} and {TileCol} are row and col index for tiles. The first zoom level for a product that covers the entire globe will have two columns and one row so that the URLs are as follows:

```
http://moontrek.jpl.nasa.gov/trektiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/…
http://moontrek.jpl.nasa.gov/trektiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/…
```

*(The two example tile URLs above are truncated at the right edge in the source page; the trailing `{TileMatrixSet}/{TileMatrix}/{TileRow}/{TileCol}` portion is cut off.)*

The second zoom level has four columns and two rows and so on. If the image tile is missing, that means there is no data coverage in that area. You can also use coverage Bbox to calculate the coverage before requesting image tiles.

For a complete listing of the Moon's Equirectangular, North Polar and South Polar based Services, please see [https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=moon](https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=moon)

## Available Mars Mosaics

Each mosaic below has a **Preview** link and a **WMTS Capabilities** link on the live page.

| Mosaic | Preview | WMTS Capabilities |
|--------|---------|-------------------|
| Viking Color Mosaic - Global Map | Preview | WMTS Capabilities |
| CTX Mosaic - Curiosity Landing Site | Preview | WMTS Capabilities |
| HiRISE Mosaic - Curiosity Landing Site | Preview | WMTS Capabilities |
| HiRISE Mosaic - ESP_040776_2115 | Preview | WMTS Capabilities |
| HiRISE Mosaic - ESP_042252_1930_RED_B_01_ORTHO | Preview | WMTS Capabilities |
| HiRISE Mosaic - ESP_042647_1760_RED_B_01_ORTHO | Preview | WMTS Capabilities |
| HRSC Mosaic - Martian East | Preview | WMTS Capabilities |
| HRSC Color Mosaic - MC11 | Preview | WMTS Capabilities |
| HRSC Mosaic - MC11 | Preview | WMTS Capabilities |
| HiRISE Mosaic - Spirit Landing Site | Preview | WMTS Capabilities |
| HiRISE Mosaic - Opportunity Landing Site | Preview | WMTS Capabilities |
| HiRISE Mosaic - Phoenix Landing Site | Preview | WMTS Capabilities |
| HiRISE Mosaic - Sojourner Landing Site | Preview | WMTS Capabilities |
| Albedo Mosaic - Thermal Emission Spectrometer | Preview | WMTS Capabilities |
| DEM Grayscale - Mars Orbiter Laser Altimeter | Preview | WMTS Capabilities |
| Color Hillshade - Mars Orbiter Laser Altimeter | Preview | WMTS Capabilities |
| Experience Curiosity - Curiosity Landing Site | Preview | WMTS Capabilities |
| Atlas Mosaic - Mars Orbiter Camera | Preview | WMTS Capabilities |
| Infrared Night - Thermal Emission Imaging System | Preview | WMTS Capabilities |
| Infrared Day - Thermal Emission Imaging System | Preview | WMTS Capabilities |
| HRSC Mosaic - Mawrth Vallis | Preview | WMTS Capabilities |
| HRSC Color Mosaic - Mawrth Vallis | Preview | WMTS Capabilities |

## Available Vesta Mosaics

| Mosaic | Preview | WMTS Capabilities |
|--------|---------|-------------------|
| global_LAMO | Preview | WMTS Capabilities |
| Vesta_Dawn_HAMO_DTM_DLR_Global_48ppd 8Bit | Preview | WMTS Capabilities |
| Vesta_Dawn_Geology_Global_32ppd_IAU | Preview | WMTS Capabilities |
| Vesta_Dawn_HAMO_ClrShade_DLR_Global_48ppd_IAU | Preview | WMTS Capabilities |
| Vesta_Dawn_HAMO_MinRatio_DLR_global_74ppd_IAU | Preview | WMTS Capabilities |
| Vesta_Dawn_HAMO_Shade_DLR_Global_48ppd_IAU | Preview | WMTS Capabilities |
| Vesta_Dawn_HAMO_TrueClr_DLR_global_74ppd | Preview | WMTS Capabilities |
