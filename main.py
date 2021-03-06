n_episodes = 300
max_t = 1000
eps_start = 1.0
eps_end = 0.01
eps_decay = 0.985
BETA = 0.0025

import matplotlib.pyplot as plt
# %matplotlib inline

import sys
import numpy as np
import pandas as pd
import torch
from collections import deque
import matplotlib.pyplot as plt
from agent import Agent

from mlagents.envs import UnityEnvironment


print("Python version:")
print(sys.version)

# check Python version
if (sys.version_info[0] < 3):
    raise Exception("ERROR: ML-Agents Toolkit (v0.3 onwards) requires Python 3")

# env = UnityEnvironment(file_name = "../../bonnie_envs/pyramid_1l/pyramid.x86_64")
# env = UnityEnvironment(file_name = "../../bonnie_envs/pyramid_1w/Unity Environment.exe")
env = UnityEnvironment(file_name = "../../bonnie_envs/pyramid_window/Unity Environment.exe")
# env = UnityEnvironment(file_name = "../../bonnie_envs/pyramid_linux/pyramid.x86_64")

brain_name = env.brain_names[0]
brain = env.brains[brain_name]
env_info = env.reset(train_mode=True)[brain_name]

state_size = env_info.vector_observations.shape[1]
action_size = brain.vector_action_space_size[0]
num_agents = len(env_info.agents)

agent = Agent(num_agents, state_size, action_size, seed = 0)
scores = []                        
scores_window = deque(maxlen=50)   
eps = eps_start 
done = False

for i_episode in range(n_episodes):
    env_info = env.reset(train_mode= True)[brain_name]
    states = env_info.vector_observations
    agent_score = np.zeros(num_agents)
    done = False
    for t in range(max_t):
    # while not done:
        actions = agent.act(states, eps)
        env_info = env.step(actions)[brain_name]
        next_states = env_info.vector_observations 
        rewards = env_info.rewards
        # print ("REWARDS: ", rewards)
        
        dones = env_info.local_done
        
        # r --> combined reward
        # r_int --> intrinsic reward
        # rewards --> extrinsic reward
        # r = np.zeros(num_agents)
        for i in range(num_agents):
            # r[i] = rewards[i] + BETA * r_int[i]
            agent_score[i] += rewards[i]
        
        agent.step(states, actions, rewards, next_states, dones)
        states = next_states
    
    # print (agent_score)
    score = sum(agent_score)/num_agents
    scores_window.append(score) 
    scores.append(score)
    eps = max(eps_end, eps_decay*eps) # decrease epsilon
    # print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)), end="")

    if i_episode % 10 == 0 or i_episode < 5:
        print('\rEpisode {}\tAgent Score: {:.2f}'.format(i_episode, score))
        torch.save(agent.qnetwork_local.state_dict(), 'checkpoint.pth')

    # if np.mean(scores_window) >= 1.7:
    if score >= 1.7:
        # print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)))
        print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(i_episode, score))
        torch.save(agent.qnetwork_local.state_dict(), 'checkpoint.pth')
        break

# Save figure
fig = plt.figure()
ax1 = fig.add_subplot(111)
plt.plot(np.arange(len(scores)), scores)
plt.ylabel('Score')
plt.xlabel('Episode Number')
plt.savefig('Results.png')
# Save data
df = pd.DataFrame(scores)
df.to_csv('score.csv', index=False)
print ("FIGURE + DATA SAVED")
    