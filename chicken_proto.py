class Chicken:
    def __init__(self, chicken_type, starting_node, start_offset):
        self.complete = False
        self.currentNode = starting_node
        self.startOffset = start_offset
        self.nodeProgress = 0 # Where at in the current node. Ticked up by 1 each update step
        if (chicken_type == 0):
            # baby chick
            pass
        elif (chicken_type == 1):
            # hen
            self.weight = True # Can depress pressure plates
            self.tunnel = False # Can fit in small tunnels
            self.speed = 5 # 5 units per step, so that baby chick can be slower
        elif (chicken_type == 2):
            pass
            # rooster

class Node:
    def __init__(self, id, distance, trigger_flag, check_flag, flag_state, forward_nodes, node_type):
        self.id = id
        self.distance = distance
        self.triggerFlag = trigger_flag # Does this node set a flag?
        self.checkFlag = check_flag # Which node does this check the flag of?
        # We might have multiple trigger_flags in the future, and also need to check conditions
        self.flagState = flag_state  # Is this definitionally 0 by default
        self.forwardNodes = forward_nodes # array of forward-connecting nodes. flag_state indexes the appropriate node
        self.nodeType = node_type

class MapGraph:
    def __init__(self):
        self.nodes = []

    def addNode(self, my_node):
        self.nodes.append(my_node)

def render(my_graph, my_chickens):
    # This is just going to be bespoke for my test levels at the
    #   moment, until I have some time to acutally think about it properly
    '''
    0-1-2-8-9-13
    3-4-5-6-7-8-9-13
    10-11-12-9-13
    chick1
        node: 3
        progress: 40
        node_end:60
        [|||||||  ]
    chick2
        node: 10

        [|||||||  ]
    chick3

'''
    seen = []
    print_str = ""
    for node in my_graph.nodes:
        # Assume sorted for now
        if node.id in seen:
           continue
        seen.append(node.id)
        x = node
        while (True):
            if x.nodeType == "goal":
                break
            # FIXME only taking the first path right now, because we don't actually handle real graphs
            if my_graph.nodes[x.forwardNodes[0]].id == x.id:
                continue
            # If a chicken is in this node, then colorize it
            chicken_here = False
            node_str = str(x.id) + "-"
            for chicky in my_chickens:
                if chicky.currentNode == x.id:
                    node_str = '\033[92m' + str(x.id) + '\033[0m' + "-"

            print_str += node_str
            seen.append(x.id)
            x = my_graph.nodes[x.forwardNodes[0]]
        print_str += "\n"
    print(print_str)

    for i in range(0, len(my_chickens)):
        chicken = my_chickens[i]
        node_len = my_graph.nodes[chicken.currentNode].distance
        chicken_str = "chicken {}:\n  node:{}\n  node_progress:{}\n  node_end:{}\n".format(
            i,
            chicken.currentNode,
            chicken.nodeProgress,
            node_len
        )
        percent = int(10 * chicken.nodeProgress / node_len)  # in increments of 10%
        progress_meter = ['['] + ['|' if x < percent else ' ' for x in range(0,10)] + [']']
        progress_meter = ''.join(progress_meter)
        chicken_str += progress_meter
        print(chicken_str)


def main():
    game_over = False
    graph = MapGraph()
    chickens = []

    graph.addNode(Node(0, 20, False, -1, 0, [1], "path"))
    graph.addNode(Node(1, 10, True, -1, 0, [2], "plate"))
    graph.addNode(Node(2, 50, False, -1, 0, [8], "path"))
    graph.addNode(Node(3, 30, False, -1, 0, [4, 3], "gate"))
    graph.addNode(Node(4, 10, False, 1, 0, [5], "path"))
    graph.addNode(Node(5, 10, False, -1, 0, [6], "path"))
    graph.addNode(Node(6, 10, True, -1, 0, [7], "plate"))
    graph.addNode(Node(7, 10, False, -1, 0, [8], "path"))
    graph.addNode(Node(8, 30, False, -1, 0, [9], "path"))
    graph.addNode(Node(9, 10, False, -1, 0, [13], "path"))
    graph.addNode(Node(10, 60, False, -1, 0, [11, 10], "gate"))
    graph.addNode(Node(11, 10, False, 6, 0, [12], "path"))
    graph.addNode(Node(12, 10, False, -1, 0, [9], "path"))
    graph.addNode(Node(13, 10, False, -1, 0, [], "goal"))

    chickens.append(Chicken(1, 0, 0))
    chickens.append(Chicken(1, 3, 0))
    chickens.append(Chicken(1, 10, 0))

    while game_over is False:
        # Clear flags which do not exhibit hysteresis
        for i in range(0, len(graph.nodes)):
            if graph.nodes[i].nodeType != "toggle":
                graph.nodes[i].flagState = 0
        for chicken in chickens:
            # Re-set nodes according to current state
            if graph.nodes[chicken.currentNode].triggerFlag:
                graph.nodes[chicken.currentNode].flagState = 1

        # Send out virtual chickens to evaluate triggers
        clean_flags = False
        while clean_flags is False:
            clean_flags = True
            for chicken in chickens:
                # Send out virtual chickens until flags and triggers converge
                nextNodeIdx = graph.nodes[chicken.currentNode].forwardNodes[graph.nodes[chicken.currentNode].flagState]
                nodeLen = graph.nodes[chicken.currentNode].distance
                triggerFlag = graph.nodes[nextNodeIdx].triggerFlag
                if triggerFlag and graph.nodes[nextNodeIdx].flagState == 0 and (chicken.nodeProgress + chicken.speed) >= nodeLen:
                    # Set valid triggers at next node, unset triggers from previous node if no other chickens there. There is an ambiguous condition here to make a decision on I think
                    graph.nodes[nextNodeIdx].flagState = 1
                    graph.nodes[chicken.currentNode].flagState = 0
                    clean_flags = False



        for i in range(0, 3):
            chickens[i].nodeProgress += chickens[i].speed

            current_node = graph.nodes[chicken.currentNode] # FIXME, assuming node idx = node_id for now, but this will eventually break, I'm sure
            if (chickens[i].nodeProgress >= current_node.distance):
                chickens[i].currentNode = current_node.forwardNodes[current_node.flagState]
                end_node = 12
                if chickens[i].currentNode == end_node:
                    chickens[i].complete = True
                    chickens[i].speed = 0

        # Check if the chickens are finished
        game_over = True
        for i in range(0, 3):
            if chickens[i].complete is False:
                game_over = False

        render(graph, chickens)
        import pdb;pdb.set_trace()
        # TODO wait for user input to see the next game step

    print("The chickens solved the level!")


if __name__ == "__main__":
    main()
