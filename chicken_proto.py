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
        self.node_type = node_type

class MapGraph:
    def __init__(self):
        self.nodes = []

    def addNode(self, my_node):
        self.nodes.append(my_node)


def main():
    game_over = False
    graph = MapGraph()
    chickens = []

    graph.addNode(Node(0, 20, False, -1, 0, [1], "path"))
    graph.addNode(Node(1, 10, True, -1, 0, [2], "plate"))
    graph.addNode(Node(2, 40, False, -1, 0, [8], "path"))
    graph.addNode(Node(3, 30, False, -1, 0, [4, 3], "gate"))
    graph.addNode(Node(4, 10, False, 1, 0, [5], "path"))
    graph.addNode(Node(5, 10, False, -1, 0, [6], "path"))
    graph.addNode(Node(6, 10, True, -1, 0, [7], "plate"))
    graph.addNode(Node(7, 10, False, -1, 0, [8], "path"))
    graph.addNode(Node(8, 30, False, -1, 0, [9], "path"))
    graph.addNode(Node(9, 10, False, -1, 0, [10], "path"))
    graph.addNode(Node(10, 60, False, -1, 0, [11, 10], "gate"))
    graph.addNode(Node(11, 10, False, 6, 0, [12], "path"))
    graph.addNode(Node(12, 30, False, -1, 0, [9], "path"))

    chickens.append(Chicken(1, 0, 0))
    chickens.append(Chicken(1, 3, 0))
    chickens.append(Chicken(1, 10, 0))

    while game_over is False:
        # Clear flags which do not exhibit hysteresis
        for i in range(0, len(graph.nodes)):
            if graph.nodes[i].node_type != "toggle":
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
    print("The chickens solved the level!")


if __name__ == "__main__":
    main()
