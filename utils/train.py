import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class ActorCritic(nn.Module):
    def __init__(self, num_inputs, num_outputs):
        super(ActorCritic, self).__init__()
        self.critic = nn.Sequential(
            nn.Linear(num_inputs, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

        self.actor = nn.Sequential(
            nn.Linear(num_inputs, 64),
            nn.ReLU(),
            nn.Linear(64, num_outputs),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        value = self.critic(x)
        probs = self.actor(x)
        return probs, value

class PPO:
    def __init__(self, num_inputs, num_outputs, lr=3e-4, gamma=0.99, k_epochs=4, eps_clip=0.2):
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epochs = k_epochs

        self.policy = ActorCritic(num_inputs, num_outputs)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.policy_old = ActorCritic(num_inputs, num_outputs)
        self.policy_old.load_state_dict(self.policy.state_dict())

        self.MseLoss = nn.MSELoss()

    def select_action(self, state, memory):
      state = torch.from_numpy(state).float().unsqueeze(0)
      probs, _ = self.policy_old(state)
      m = torch.distributions.Categorical(probs)
      action = m.sample()
      memory.states.append(state)
      memory.actions.append(action)
      memory.logprobs.append(m.log_prob(action))
  
      return action.item()


    def update(self, memory):
  
      rewards = torch.tensor(memory.rewards)
      old_states = torch.stack(memory.states).squeeze(1).detach()
      old_actions = torch.stack(memory.actions).detach()
      old_logprobs = torch.stack(memory.logprobs).detach()
  
      rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-7)
  
      # Optimize policy for K epochs
      for _ in range(self.k_epochs):
          # Evaluating old actions and values
          logprobs, state_values = self.policy(old_states)
          dist_entropy = -(logprobs * torch.exp(logprobs)).sum(-1).mean()
          
          # Match state_values tensor dimensions with rewards tensor
          state_values = torch.squeeze(state_values)
  
          # Finding the ratio (pi_theta / pi_theta__old)
          ratios = torch.exp(logprobs - old_logprobs.detach())
  
          # Finding Surrogate Loss
          advantages = rewards - state_values.detach()
          surr1 = ratios * advantages
          surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip) * advantages
          loss = -torch.min(surr1, surr2) + 0.5 * self.MseLoss(state_values, rewards) - 0.01 * dist_entropy
  
          # Take gradient step
          self.optimizer.zero_grad()
          loss.mean().backward()
          self.optimizer.step()
      
      # Copy new weights into old policy
      self.policy_old.load_state_dict(self.policy.state_dict())


# Memory class to store the rewards, actions, and states
class Memory:
    def __init__(self):
        self.actions = []
        self.states = []
        self.logprobs = []
        self.rewards = []
        self.is_terminals = []

    def clear_memory(self):
        del self.actions[:]
        del self.states[:]
        del self.logprobs[:]
        del self.rewards[:]
        del self.is_terminals[:]

def train():
    env = RobotouilleWrapper(your_env, your_config)
    num_inputs = env.observation_space.shape[0]  
    num_outputs = env.action_space.n  

    ppo_agent = PPO(num_inputs, num_outputs)
    memory = Memory()

    # Training loop
    max_episodes = 500 
    for episode in range(max_episodes):
        state = env.reset()
        for t in range(1000):  
            action = ppo_agent.select_action(state, memory)
            state, reward, done, _ = env.step(action)
            
            # Save data in memory
            memory.rewards.append(reward)
            memory.is_terminals.append(done)

            if done:
                break
        
        ppo_agent.update(memory)
        memory.clear_memory()

        if episode % 10 == 0:
            pass

if __name__ == "__main__":
    train()
