import gym
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient
from datetime import datetime

class OptSBEnv(gym.Env):
    def __init__(self): #required for env
        self.action_space = gym.spaces.Discrete(5)
        #self.observation_space = gym.spaces.Discrete(2)
        self.client = None
        self.bucket = None
        self.obs_type = 'sim'
        self.obs = 0.
        self.reward = 0.
        self.state = None

    def step(self, action): #required for env
        self.state = self._get_observation()
    
        if action == 1:
            self.reward = 1
        else:
            self.reward = -2
            
        done = True
        info = {}
        return self.state, self.reward, done, info

    def reset(self): #required for envs
        self.obs = 0.
        self.reward = 0.

        self.state = self._get_observation()
        
    def _process_data(self): #manipulate obs data??
        data = 10.

    def _get_observation(self): #pull data from database (sim or exp)??
        #if sim, run sim -> save to db -> pull from db
        #if exp, pull from db
        if (self.obs_type=='sim'):
            self._run_simulation()
        
        #pull from database
        db_read = self._pull_database()
        self.obs = db_read
        return self.obs
    
    def _run_simulation(self): #process track
        print("inside _run_simulation")
        #call function for sps_line to run in new dir and save data to db
        #create dummy data in db for now
        if (self.client) :
            for i in range(1):
                data = [ Point('Data').tag("type","detector").tag("location","target")
                .field("pos1",i).field("pos2",2.).field("rate1",i+1.).field("rate2",6.)
                .time(time=datetime.utcnow()) ]
                self.client.write_data(data)
        else:
            print("client not connected?")

    def client_connect(self,client, bucket):
        self.client = client
        self.bucket = bucket
        # return self.client

    def _pull_database(self): #pull 'obs' from correct influxdb
        #time1 = uint(v: 2019-09-17T21:12:05Z)
        if (self.client) :
            query = f'from(bucket: "{self.bucket}") \
            |> range(start: -1m) \
            |> filter(fn: (r) => r["_measurement"] == "Data")'
            return self.client.query_data(query)
        else:
            return None

    def _calculate_reward(self, action): # if needed beyond what is inside step
        self.reward = 10.
    
    def render(self, mode='human'): #decide what to draw from env
        print("draw env figs")
        # fig = go.Figure()