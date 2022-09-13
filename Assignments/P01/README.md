## Project 1
#### 9/8/2022
# 
## API for Finding Data About Volcanoes Across the World Stored in a PostgreSQL Database.
#### Description: 

This API searches a database containing volcanic data and can be used to perform three different
types of queries: find_All, find_One, and find_Closest. find_All shows every volcano and its data to
the user. find_One finds a volcano that meets the given specifications defined by the user. This can be
the name of a country, a volcano's hazardness, whether it's active, and more. The route will show the
user the first volcano that meets the user's specifications. find_Closest takes a given set of 
latitude and longitude lines and will display the volcano closest to the given coordinates. For more
information about volcanoes see: [Global Distribution of Volcanism](https://www.preventionweb.net/english/hyogo/gar/2015/en/bgdocs/risk-section/GVMd.%20Global%20Volcanic%20Hazards%20and%20Risk%20Country%20volcanic%20hazard%20and%20risk%20profiles..pdf)


#### Instruction:

To run this program type: <u>python main.py</u> into your terminal and then go to <u>localhost:8080</u>
to view the API server and query the volcanic data.
