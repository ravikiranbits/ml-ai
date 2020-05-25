# Import routines

import numpy as np
import math
import random

# Defining hyperparameters
m = 5 # number of cities, ranges from 1 ..... m
t = 24 # number of hours, ranges from 0 .... t-1
d = 7  # number of days, ranges from 0 ... d-1
C = 5 # Per hour fuel and other costs
R = 9 # per hour revenue from a passenger


class CabDriver():

    def __init__(self):
        #"""initialise your state and define your action space and state space"""
        self.action_space = [(start,stop) for start in range(m) for stop in range(m) if start != stop]
        self.action_space = [(0,0)]+self.action_space #Add action (0,0) to the action space
        self.state_space = [(start,time,day) for start in range(m) for time in range(t) for day in range(d)]
        self.state_size = m+t+d
        self.action_size = len(self.action_space)
        
        self.total_time = 0
        self.max_time = 720   #30 days = 24*30

        # Start the first round
        self.reset()


    ## Encoding state (or state-action) for NN input

    def state_encod_arch1(self, state):
        #"""convert the state into a vector so that it can be fed to the NN. This method converts a given state into a vector format. Hint: The vector is of size m + t + d."""
        state_encod = np.array([0 for x in range(m+t+d)])
        state_encod[state[0]] = 1
        state_encod[m+state[1]] = 1
        state_encod[m+t+state[2]] = 1

        return state_encod


    # Use this function if you are using architecture-2 
    # def state_encod_arch2(self, state, action):
    #     """convert the (state-action) into a vector so that it can be fed to the NN. This method converts a given state-action pair into a vector format. Hint: The vector is of size m + t + d + m + m."""

        
    #     return state_encod


    ## Getting number of requests

    def requests(self, state):
        #"""Determining the number of requests basis the location. 
        #Use the table specified in the MDP and complete for rest of the locations"""
        location = state[0]
        if location == 0:
            requests = np.random.poisson(2)
        if location == 1:
            requests = np.random.poisson(12)
        if location == 2:
            requests = np.random.poisson(4)
        if location == 3:
            requests = np.random.poisson(7)
        if location == 4:
            requests = np.random.poisson(8)
        if requests >15:
            requests = 15

        possible_actions_index = random.sample(range(1, (m-1)*m +1), requests) # (0,0) is not considered as customer request
        #print(possible_actions_index)
        #print(len(self.action_space))
        #for i in possible_actions_index:
        #    print(self.action_space[i])
        actions = [self.action_space[i] for i in possible_actions_index]

        # [0, 0] is not a 'request', but it is one of the possible actions
        possible_actions_index.append(0)
        actions.append((0,0))

        return possible_actions_index,actions   



    def reward_func(self, state, action, Time_matrix):
        #"""Takes in state, action and Time-matrix and returns the reward"""
        if action == (0,0):
            reward = -1*C
        else:
            pickuptime = int(state[1] + Time_matrix[state[0]][action[0]][state[1]][state[2]])
            pickupday = state[2]
            if pickuptime >= 24:
                pickuptime = int(pickuptime - 24)
                pickupday = pickupday + 1
                if pickupday >= 7:
                    pickupday = pickupday - 7
            
            reward = R*Time_matrix[action[0]][action[1]][pickuptime][pickupday] - C*(Time_matrix[action[0]][action[1]][pickuptime][pickupday] + Time_matrix[state[0]][action[0]][state[1]][state[2]])
        return reward




    def next_state_func(self, state, action, Time_matrix):
        #"""Takes state and action as input and returns next state"""
        
        if action == (0,0):
            # when action is (0,0)
            dropofflocation = state[0]
            time_elapsed = 1            
            dropofftime = state[1] + 1
            dropoffday = state[2]
        else:
            dropofflocation = action[1]
            pickuptime = int(state[1] + Time_matrix[state[0]][action[0]][state[1]][state[2]])
            pickupday = state[2]
            if pickuptime >= 24:
                pickuptime = int(pickuptime - 24)
                pickupday = pickupday + 1
                if pickupday >= 7:
                        pickupday = pickupday - 7
            #print(action[0],action[1],pickuptime,pickupday)
            dropofftime = int(pickuptime + Time_matrix[action[0]][action[1]][pickuptime][pickupday])
            dropoffday = pickupday            
            time_elapsed = int(Time_matrix[action[0]][action[1]][pickuptime][pickupday] + Time_matrix[state[0]][action[0]][state[1]][state[2]])
        
        if dropofftime >= 24:
            dropofftime = int(dropofftime - 24)
            dropoffday = dropoffday + 1
            if dropoffday >= 7:
                    dropoffday = dropoffday - 7
                    
        self.total_time = self.total_time + time_elapsed
        
        # check whether it is a terminal state
        if (self.total_time >= self.max_time):
            terminal_state = 1
            self.total_time = 0
        else:
            terminal_state = 0
            
        terminal_state = bool(terminal_state) # returns terminal state as True or False
        
        next_state = (dropofflocation,dropofftime,dropoffday)
        
        return next_state, terminal_state


    def reset(self):
        self.state_init = self.state_space[np.random.choice(len(self.state_space))]
        return self.state_init