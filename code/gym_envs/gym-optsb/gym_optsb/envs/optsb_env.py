import gym
class OptSBEnv(gym.Env):
    def __init__(self): #required for env
        self.action_space = gym.spaces.Discrete(5)
        self.observation_space = gym.spaces.Discrete(2)

    def step(self, action): #required for env
        state = 1
    
        if action == 1:
            reward = 1
        else:
            reward = -1
            
        done = True
        info = {}
        return state, reward, done, info

    def reset(self): #required for env
        state = 0
        return state

    def _process_data(self): #manipulate obs data??
        data = 10

    def _get_observation(self): #pull data from database (sim or exp)??
        state = 10
        return state

    def _calculate_reward(self, action): # if needed beyond what is inside step
        reward = 10
    
    def render(self, mode='human'): #decide what to draw from env
        print("draw env figs")
        # fig = go.Figure()
        # fig.add_trace(go.Scatter(x=self.df.index, y=self.df['Low']))
        # fig.add_trace(go.Scatter(x=self.df.index, y=self.df['High'],fill='tonexty'))
        # fig.add_trace(go.Scatter(x=self.df.index, y=self.df['Adj Close']))
        # fig.update_xaxes(title='Price')
        # fig.show()