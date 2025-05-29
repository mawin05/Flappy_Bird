import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from dqn import DQN
from ReplayBuffer import ReplayBuffer
class Agent:
    def __init__(self, input_dim, output_dim):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy = DQN(input_dim, output_dim).to(self.device) # warstwa danych wejściowych
        self.target = DQN(input_dim, output_dim).to(self.device) # warstwa danych wyjściowych (Nic nie rób, albo skacz)
        self.target.load_state_dict(self.policy.state_dict()) # kopiujemy policy do target

        self.alpha = 0.001 # learning rate
        self.gamma = 0.9 # discount rate
        self.network_sync_rate = 1000 # liczba kroków, która jest potrzeba do synchronizacji target z policy
        self.replay_buffer = ReplayBuffer(10000) # inicjalizacja buffora pamięci
        self.batch_size = 64 # wielkośc próbek jakie będziemy losowo wybierać z buffora pamięci do trenowania policy
        self.cost_function = nn.MSELoss() # funkja do oceny rozbieżności między obecnym stanem policy a oczekiwanym
        self.optimizer = optim.Adam(self.policy.parameters(), lr=self.alpha) # aktualizuje wagi i biasy sieci neuronowej
        # aby zmniejszyć obliczony cost, robi to na podstawie gradientów wyliczych w backward()
        self.epsilon = 1.0 # wskaźnik eksploracji
        self.epsilon_min = 0.01 # minimalna eksploracja
        self.epsilon_decay = 0.995 # spadek eksploracji
        self.train_step_counter = 0 # licznik kroków

    def select_action(self, state):
        # jeżeli losowa liczba jest mniejsza niż wskaźnik eksploracji
        # to wybieramy losową akcję
        # w przeciwnym wypadku wybieramy najlepszą akcję na podstawie policy
        if random.random() < self.epsilon:
            return random.randint(0, 1)
        else:
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.policy(state)
            return q_values.argmax().item()

    def train(self):
        if len(self.replay_buffer) < self.batch_size:
            return # nie trenujemy dopóki nie mamy wystarczającej liczby doświadczeń

        # pobieramy losowo wybrane dane dotyczących akcji i ich konsekwencji z bufora pamięci
        states, actions, new_states, rewards, dones = self.replay_buffer.sample(self.batch_size)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        new_states = torch.FloatTensor(new_states).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        # obliczamy wartości dla neuronów wyjściowych reprezentujących wybrane akcje
        q_values = self.policy(states).gather(1, actions)

        # obliczamy docelowe wartości q: reward + gamma * max(Q(next_state)) * (1 - done)
        with torch.no_grad():
            next_q_values = self.target(new_states).max(1, keepdim=True)[0]
            targets = rewards + self.gamma * next_q_values * (1 - dones)

        # obliczamy cost
        cost = self.cost_function(q_values, targets)

        # aktualizacja wag i biasów na podstawie cost (propagacja wsteczna)
        self.optimizer.zero_grad()
        cost.backward()
        self.optimizer.step()

        # zmniejszenie wskaźnika eksploracji
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        self.train_step_counter += 1
        # aktualizacja target co X kroków
        if self.train_step_counter % self.network_sync_rate == 0:
            self.update_target()

    def update_target(self):
        self.target.load_state_dict(self.policy.state_dict())
