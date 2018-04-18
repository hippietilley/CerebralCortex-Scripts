from data_replay.db_helper_methods import SqlData
import os
import json
import yaml
from cerebralcortex.cerebralcortex import CerebralCortex
from cerebralcortex.core.datatypes.datapoint import DataPoint
from cerebralcortex.core.datatypes.datastream import DataStream
import statistics
from datetime import datetime
import uuid
import argparse
from haversine import haversine

class SqlToCCStream():
    def __init__(self, config):

        self.CC = CerebralCortex(config)
        self.config = self.CC.config
        self.sqlData = SqlData(self.config, dbName="environmental_data_collection")
        self.process()

    def process(self):
        user_ids = self.filter_user_ids()
        # get all locations lats/longs
        all_locations = self.sqlData.get_latitude_llongitude()
        with open("weather_data.json", "r") as wd:
            metadata = wd.read()
        metadata = json.loads(metadata)
        input_stream_name = 'LOCATION--org.md2k.phonesensor--PHONE'
        for uid in user_ids:
            stream_ids = self.CC.get_stream_id(uid, input_stream_name)

            # TEST CODE
            # location_id = self.get_location_id((37.439168,-122.086283), all_locations)
            # day = datetime.strptime("20171221", "%Y%m%d").strftime("%Y-%m-%d")
            # weather_data = self.sqlData.get_weather_data_by_city_id(location_id, day)
            # dps = []
            # for wd in weather_data:
            #     wd["temperature"] = json.loads(wd["temperature"])
            #     wd["wind"] = json.loads(wd["wind"])
            #     wd["humidity"] = int(wd["humidity"])
            #     wd["clouds"] = int(wd["clouds"])
            #     dps.append(DataPoint(wd["start_time"], None, None, wd))

            for sid in stream_ids:
                days = self.CC.get_stream_days(sid)
                for day in days:
                    output_stream_id=""
                    # get gps data from stream-name 'LOCATION--org.md2k.phonesensor--PHONE'
                    location_stream = self.CC.get_stream(sid, day)

                    # compute median on lat. and long. vals
                    user_loc = self.compute_lat_long_median(location_stream.data)
                    offset = location_stream.data[0].offset
                    # get weather data for match lat/long values
                    location_id = self.get_location_id(user_loc, all_locations)

                    if location_id is not None:
                        formated_day = datetime.strptime(day, "%Y%m%d").strftime("%Y-%m-%d")
                        weather_data = self.sqlData.get_weather_data_by_city_id(location_id, formated_day)

                        # convert data into datastream
                        execution_context = metadata["execution_context"]
                        input_streams_metadata = {"id":sid, "name":input_stream_name}
                        metadata["execution_context"]["processing_module"]["input_streams"] \
                            = input_streams_metadata
                        dps = []
                        for wd in weather_data:
                            wd["temperature"] = json.loads(wd["temperature"])
                            wd["wind"] = json.loads(wd["wind"])
                            wd["humidity"] = int(wd["humidity"])
                            wd["clouds"] = int(wd["clouds"])

                            dps.append(DataPoint(wd["start_time"], None, offset, wd))
                        # generate UUID for stream
                        output_stream_id = str(metadata["data_descriptor"])+str(execution_context)+str(metadata["annotations"])
                        output_stream_id += "weather-data-stream"
                        output_stream_id += "weather-data-stream"
                        output_stream_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, output_stream_id))
                        ds = DataStream(identifier=output_stream_id, owner=uid, name=metadata["name"], data_descriptor=metadata["data_descriptor"], execution_context=execution_context, annotations=metadata["annotations"], data=dps)

                        # store data stream
                        self.CC.save_stream(ds)


    def compute_lat_long_median(self, data):
        latitude = []
        longitude = []
        for dp in data:
            latitude.append(dp.sample[0])
            longitude.append(dp.sample[1])
        return statistics.median(latitude),statistics.median(longitude)

    def get_location_id(self, user_loc, all_locations):
        # find distance between user location and weather lat/long
        closest = None
        location_id = None
        for loc in all_locations:
            distance = haversine(user_loc,(float(loc["latitude"]),float(loc["longitude"])),miles=True)
            if closest is None:
                closest = distance
                location_id = loc["id"]
            elif distance<closest:
                closest = distance
                location_id = loc["id"]
        if closest<=15: #if distance is below then 15 miles then select it as weather location
            return location_id
        else:
            return None

    def filter_user_ids(self):

        active_users = []
        all_users = []
        for uid in self.CC.get_all_users("mperf"):
            all_users.append(uid["identifier"])

        data_dir = self.config["data_replay"]["data_dir"]
        for owner_dir in os.scandir(data_dir):
            if owner_dir.name in all_users:
                active_users.append(owner_dir)

        return active_users

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='CerebralCortex - Weather data importer')
    parser.add_argument('-conf','--conf', help='CerebralCortex configuration file', required=True)

    args = vars(parser.parse_args())

    with open(args["conf"]) as ymlfile:
        config = yaml.load(ymlfile)


    SqlToCCStream(args["conf"])
