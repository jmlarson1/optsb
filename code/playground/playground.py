#%%
import gym
import gym_optsb
# %%
env = gym.make("optsb-v0")
# %%
env.reset()
# %%

for i in range(4):
    state, reward, done, info = env.step(i)
    print(reward)

# %%
