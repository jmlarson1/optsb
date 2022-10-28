import gym
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient
from datetime import datetime
from run_track import RunTRACK
import pandas as pd
import random
import numpy as np
import plotly.graph_objects as go
from typing import Optional

class OptSBEnv(gym.Env):
    def __init__(self): #required for env
        self.client = None
        self.bucket = None
        self.obs_type = 'sim'
        self.optimal_reward_value = -0.1
        self.reward_type = 1
        self.quad_vals = np.array([0.,0.,0.])
        self.obs = pd.DataFrame()
        self.min_action = np.array([0.0,-1.0,0.0])
        self.max_action = np.array([1.0,0.0,1.0])
        self.max_quad_val = np.array([2000.0,0.000,2000.])
        self.min_quad_val = np.array([0.0,-2000.0,0.0])
        self.delta_quad_val = np.array([50.0,50.0,50.0])
        self.action_space = gym.spaces.Box(low=-1., high=1., shape=(3,), dtype=np.float32)
        #self.action_space = gym.spaces.Discrete(6)
        self.action = np.zeros(3) #-1. #6 up/down for each
        #print(self.action)
        self.observation_space = gym.spaces.Box(low=-np.inf,high=np.inf, shape=(6,), dtype=np.float64)
        #print('State space dim is: ', self.observation_space)
        self.reward = 0.
        self.cummulative_reward = []
        self.iteration_reward = [] #reward
        self.iteration_transmission = [] #trans fraction
        self.iteration_radius = [] # x,y,r
        self.iteration_quad_vals = [] # 1,2,3
        self.iteration_action = [] #index 0-5
        self.iteration_beam_vals = [] # beam stuff
        self.state = np.ones(self.observation_space.shape[0])
        self.rs = RunTRACK()

    def step(self, action: np.ndarray): #required for env
        #apply action, get updated state
        done = False
        for i in range(len(self.action)):
            self.action[i] = action[i] * self.delta_quad_val[i]
        print("Action: ",self.action)
        self.state, state_done = self._get_observation()
        self.iteration_quad_vals.append(self.state[:3].tolist())
        #print("quad val for print: {}".format(self.iteration_quad_vals))
        # print("slice {}".format(self.iteration_quad_vals[0][2]))
        self.iteration_beam_vals.append(self.state[3:].tolist())
        #print("beam vals: {}".format(self.iteration_beam_vals))
        self.reward, reward_done = self._calculate_reward()
        self.iteration_reward.append(self.reward)
        self.cummulative_reward.append(sum(self.iteration_reward))

        if (reward_done or state_done):
            done = True
        info = {"action" : self.action, "state" : self.state, "reward" : self.reward}
        return self.state, self.reward, done, info

    def reset(self,*,seed: Optional[int] = None,return_info: bool = False,options: Optional[dict] = None,): #required for envs
        self.obs = pd.DataFrame()
        self.reward = 0.
        self.iteration_reward = [] #reward
        self.iteration_transmission = [] #trans fraction
        self.iteration_radius = [] # x,y,r
        self.iteration_quad_vals = [] # 1,2,3
        self.iteration_action = [] #index 0-8
        self.iteration_beam_vals = []
        self.action = np.zeros(3) # u/d actions x3 quads
        self.quad_vals = self.rs.get_quad_vals() #set random starting vals
        self.state, _ = self._get_observation()
        return self.state

    # def get_action_from_qvals(self,qvalues):
    #     self.action = -1 #np.zeros_like(qvalues)
    #     self.action = np.argmax(qvalues)
    #     return self.action
    
    def get_optimal_reward_value(self):
        return self.optimal_reward_value

    def _get_observation(self): #pull data from database (sim or exp)??
        #if sim, run sim -> get vals directly
        #if exp, pull from db
        if (self.obs_type=='sim'):
            db_read, obs_done = self._run_simulation() #returns many values
            self.obs = db_read[['Q1','Q2','Q3','Xrms','Yrms','part_left']]
             #pick some to send as state
        else: #not functional yet for data
            db_read = self._pull_database() 
            self.obs = db_read
        np_obs = np.squeeze(np.array(self.obs.values.tolist()))
        return np_obs, obs_done
    
    def _run_simulation(self): #process track
        df_results = pd.DataFrame()
        sim_done = False
        run_dir = self.rs.set_dir()
        print("Before: ",self.quad_vals)
        for qnum in range(len(self.quad_vals)):
            self.quad_vals[qnum] = self.quad_vals[qnum] + self.action[qnum]
            #quad val check to set "done"
            if self.quad_vals[qnum] > self.max_quad_val[qnum] or self.quad_vals[qnum] < self.min_quad_val[qnum]:
                sim_done = True
        new_quad_vals = self.quad_vals
        print("After: ",new_quad_vals)
        self.rs.set_track(run_dir,new_quad_vals)
        self.rs.run_track(run_dir)
        df_beam,df_coord,df_step = self.rs.get_output(run_dir)
        self.rs.plot_track(df_beam,df_coord,df_step,new_quad_vals)
        #should make below more digestible for selecting obs values
        #could also choose to pull data from other "z" positions
        #now just pulling very last point at the "target" position
        df_temp = pd.DataFrame({'run_dir' : [run_dir],
        'Q1': [new_quad_vals[0]], 'Q2': [new_quad_vals[1]], 'Q3': [new_quad_vals[2]],
        'Xrms': [df_beam['x_rms[cm]'].values[len(df_beam.index)-1]], 
        'Yrms': [df_beam['y_rms[cm]'].values[len(df_beam.index)-1]],
        'ax': [df_beam['a_x'].values[len(df_beam.index)-1]], 
        'ay': [df_beam['a_y'].values[len(df_beam.index)-1]],
        'az': [df_beam['a_z'].values[len(df_beam.index)-1]],
        'part_lost': [df_beam['#of_part_lost'].values[len(df_beam.index)-1]],
        'part_left': [df_beam['#of_part_left'].values[len(df_beam.index)-1]]
        })
        df_results = pd.concat([df_results,df_temp])
        #print(df_results['Q1'])
        return df_results, sim_done
       

    def client_connect(self,client, bucket):
        self.client = client
        self.bucket = bucket

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
        #general stuff
        reward_value = 0.
        factor = 100.
        xrms = self.obs.iloc[0]['Xrms']
        yrms = self.obs.iloc[0]['Yrms']
        radius_squared = xrms*xrms + yrms*yrms
        self.iteration_radius.append([xrms,yrms,radius_squared])
        transmission_fraction = self.obs.iloc[0]['part_left']/1000.
        self.iteration_transmission.append(transmission_fraction)
        if (transmission_fraction < 0.1):
            transmission_fraction = 0.1
            reward_done = True

        if (self.reward_type == 0): #reward from XY size
            reward_value = -1.*radius_squared - factor*(1.-transmission_fraction)
            reward_done = False
        if (self.reward_type == 1): #reward from transmission only
            reward_value = -(1.-transmission_fraction)
            reward_done = False
        if ( any(i == 1999. for i in self.quad_vals) ):
            reward_value-=1.
            reward_done = True
        if ( any(i == -1999. for i in self.quad_vals) ):
            reward_value-=1.
            reward_done = True
        if ( any(i == 0. for i in self.quad_vals) ):
            reward_value-=1.
            reward_done = True
        if (reward_value > self.optimal_reward_value):
            reward_done = True
        return reward_value, reward_done
    
    def render(self, mode="human"): #decide what to draw from env
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='XY',x=self.obs['Xrms'],y=self.obs['Yrms']))
        fig.show()