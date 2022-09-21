## Project 2
#### 9/20/2022
# 
## Small Project For Reading in and Querying Large Spatial Data
#### Description: 

This folder holds large datatables, each one containing its respective spatial data. It also contains the queries used to make each table and creating an index based
on the geometry column. All but the airports table was derived from shp files. The airport data was taken and cleaned from a csv file. The following datasets contained in their own postgresql datatables are:

|   #   | Table Name | Description |
| :---: | ----------- | ---------------------- |
|  01  | Airports |Dataset containing all airport locations around the world. Contains the country, name, three-code, etc. |
|  02  | Military Bases |Dataset containing all US military base locations around the world. Contains the area id, name, mtfcc, etc. |
|  03  | Primary Roads |Dataset containing all major roads within the United States. Contains the name, rttyp, mtfcc, etc. |
|  04  | Railroads |Dataset containing all railroads located in the United States. Contains the name of each railroad plus other info |
|  05  | States |Dataset containing all States and their geometries within the US. Contains the state name, its shape, etc. |
|  06  | Timezones |Dataset containing all timezone locations around the world. Contains the country, name, utc-format, etc. |
