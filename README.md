# Music Recommender
A Music Recommender API based on sample user data.
## Running
Please copy and paste user song info into the uvi_src folder with the name song_meta.json before running docker-compose  
A sample user song info  can be downloaded from the following link  
https://drive.google.com/file/d/1tBiTeFrXXMS7hqIPp4lJIyg0Cq-Ufym5/view?usp=sharing

To build it you need Docker and then you run the following command
```shell
docker-compose up
```
In a different terminal window you can call the requests to the API  
The API Manual is stored as api_manual.yaml in the uvi_src folder. The JSON output is found by running the following in the terminal
```shell
curl -X GET "http://localhost:8080/v2/"
```
