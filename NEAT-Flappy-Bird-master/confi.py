[NEAT]
fitness_criterion     = max #cosider how to eliminate the worst bird or determine the best birds..here we choose the best birds by choosing max
fitness_threshold     = 100 #what fitness level you want to reach before terminating the program
pop_size              = 50
reset_on_extinction   = False

[DefaultGenome] #we call all our population birds as genome..properties are nodes and genes...nodes are like the input and output and the genes are the connections
# node activation options
activation_default      = tanh
activation_mutate_rate  = 0.0 #if you want to change the activation function in between randomly
activation_options      = tanh

# node aggregation options..
aggregation_default     = sum
aggregation_mutate_rate = 0.0
aggregation_options     = sum
#these are the intitial connections that we have and how likely they are to change
# node bias options
bias_init_mean          = 0.0 
bias_init_stdev         = 1.0
bias_max_value          = 30.0 #the max value that can be picked
bias_min_value          = -30.0 #the min value that we can pick
bias_mutate_power       = 0.5
bias_mutate_rate        = 0.7 #how likely the population is going to change 
bias_replace_rate       = 0.1

# genome compatibility options
compatibility_disjoint_coefficient = 1.0
compatibility_weight_coefficient   = 0.5

# connection add/remove rates
conn_add_prob           = 0.5 #how likely we are to add a connection 
conn_delete_prob        = 0.5 #how likely we are to remove a connection

# connection enable options
enabled_default         = True #by default we are going to have all the connections active
enabled_mutate_rate     = 0.01

feed_forward            = True
initial_connection      = full #we will have fully connected system at the start

# node add/remove rates
node_add_prob           = 0.2 #chance of adding new nodes 
node_delete_prob        = 0.2 #chance of deleting old nodes

# network parameters
num_hidden              = 0
num_inputs              = 3 #3 input neurons
num_outputs             = 1 #1 output neuron

# node response options
response_init_mean      = 1.0
response_init_stdev     = 0.0
response_max_value      = 30.0
response_min_value      = -30.0
response_mutate_power   = 0.0
response_mutate_rate    = 0.0
response_replace_rate   = 0.0

# connection weight options
weight_init_mean        = 0.0
weight_init_stdev       = 1.0
weight_max_value        = 30
weight_min_value        = -30
weight_mutate_power     = 0.5
weight_mutate_rate      = 0.8
weight_replace_rate     = 0.1

[DefaultSpeciesSet]
compatibility_threshold = 3.0

[DefaultStagnation]
species_fitness_func = max #we are going t opt for the max fitness among the species
max_stagnation       = 20
species_elitism      = 2

[DefaultReproduction]
elitism            = 2
survival_threshold = 0.2
