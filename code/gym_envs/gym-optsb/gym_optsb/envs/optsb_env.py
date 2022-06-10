import gym
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient
from datetime import datetime
from run_track import RunTRACK
import pandas as pd
import random
import numpy as np

class OptSBEnv(gym.Env):
    def __init__(self): #required for env
        self.client = None
        self.bucket = None
        self.obs_type = 'sim'
        self.action = [0.,0.,0.,0.,0.,0.,0.,0.,0.] #change action space to 9 values?, up/down/same for each
        #yes, then apply action to get new values i.e., pick max for each magnet then apply
        self.quad_vals = [0.,0.,0.]
        self.obs = pd.DataFrame()
        self.observation_space = 6 #need to setup dynamic variable #add quad values to state?
        self.action_space = int(len(self.action)) #9
        self.reward = 0.
        self.total_reward = 0.
        self.state = None
        self.rs = RunTRACK()

    def step(self, action): #required for env
        #apply action, get updated state
        self.action = action
        self.state = self._get_observation()
        self.reward = self._calculate_reward()            
        done = True
        info = {"action" : self.action, "state" : self.state.to_numpy(), "reward" : self.reward}
        return self.state, self.reward, done, info

    def reset(self): #required for envs
        self.obs = pd.DataFrame()
        self.reward = 0.
        self.action = [0.,0.,0.,0.,0.,0.,0.,0.,0.] # [[0,1,2],[0,1,2],[0,1,2]] u/d/s action 
        self.quad_vals = self.rs.get_quad_vals() #set random starting vals
        self.state = self._get_observation()
        return self.state
    
    def querry_action(self):
        print("RANDOM")
        random_actions = np.random.uniform(0., 1., 9)
        self.action = np.zeros_like(random_actions)
        #print(random_actions)
        self.action[np.argmax(random_actions)] = 1.
        # self.action[np.argmax(random_actions[0:2])] = 1
        # self.action[np.argmax(random_actions[3:5]) + 3] = 1
        # self.action[np.argmax(random_actions[6:8]) + 6] = 1
        #print(self.action)
        return self.action #self.rs.get_quad_vals() #[1100,-1900,1200]
    
    def get_action(self,qvalues):
        self.action = np.zeros_like(qvalues)
        #print("NN: {}".format(qvalues))
        self.action[np.argmax(qvalues)] = 1.
        #print("NN Action: {}".format(self.action))
        return self.action

    def _get_observation(self): #pull data from database (sim or exp)??
        #if sim, run sim -> save to db -> pull from db
        #if exp, pull from db
        if (self.obs_type=='sim'):
            db_read = self._run_simulation() #returns many values
            self.obs = db_read[['Q1','Q2','Q3','Xrms','Yrms','part_left']] #pick some to send as state
        else: #not functional yet for data
            db_read = self._pull_database() 
            self.obs = db_read

        return self.obs
    
    def _run_simulation(self): #process track
        #print("inside _run_simulation")
        df_results = pd.DataFrame()
        run_dir = self.rs.set_dir()
        #quad_vals = self.rs.get_quad_vals() #[1100,-1900,1200]
        new_quad_vals = self.rs.mod_quad_vals(self.action, self.quad_vals) #quad_vals = apply_action()
        #print(new_quad_vals)
        self.rs.set_track(run_dir,new_quad_vals)
        self.rs.run_track(run_dir)
        df_beam,df_coord,df_step = self.rs.get_output(run_dir)
        self.rs.plot_track(df_beam,df_coord,df_step,new_quad_vals)
        #should make below more digestible for selecting obs values
        #could also choose to pull data from other "z" positions
        #now just pulling very last point at the "target"
        df_temp = {'run_dir' : run_dir,
        'Q1': new_quad_vals[0], 'Q2': new_quad_vals[1], 'Q3': new_quad_vals[2],
        'Xrms': df_beam['x_rms[cm]'].values[len(df_beam.index)-1], 
        'Yrms': df_beam['y_rms[cm]'].values[len(df_beam.index)-1],
        'ax': df_beam['a_x'].values[len(df_beam.index)-1], 
        'ay': df_beam['a_y'].values[len(df_beam.index)-1],
        'az': df_beam['a_z'].values[len(df_beam.index)-1],
        'part_lost': df_beam['#of_part_lost'].values[len(df_beam.index)-1],
        'part_left': df_beam['#of_part_left'].values[len(df_beam.index)-1]
        }
        df_results = df_results.append(df_temp, ignore_index = True)
        return df_results
       

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

    def _calculate_reward(self): # if needed beyond what is inside step
        #reward from XY size
        reward_value = 0.
        xrms = self.obs.iloc[0]['Xrms']
        yrms = self.obs.iloc[0]['Yrms']
        radius_squared = xrms*xrms + yrms*yrms
        transmission_fraction = self.obs.iloc[0]['part_left']/1000.0
        factor = 20.
        reward_value = 1./radius_squared + factor*transmission_fraction
        return reward_value
    
    def render(self, mode='human'): #decide what to draw from env
        print("draw env figs")
        # fig = go.Figure()