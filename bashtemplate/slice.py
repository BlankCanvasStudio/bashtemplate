import bashparse, copy


# This could be an interesting idea
def visit_children(nodes, function):
    pass


class Slice:
    def __init__(self, variable_name, start_path, end_path):
        self.name = variable_name 
        self.start = start_path
        self.end = end_path
    def __repr__(self):
        start = end = "None"
        if self.start: start = '[' + ','.join(str(x) for x in self.start) + ']'
        if self.end: end = '[' + ','.join(str(x) for x in self.end) + ']'
        return "Slice(" + self.name + ', ' + start + ', ' + end + ')'
    def __str__(self):
        start = end = "None"
        if self.start: start = '[' + ','.join(str(x) for x in self.start) + ']'
        if self.end: end = '[' + ','.join(str(x) for x in self.end) + ']'
        return "Slice(" + self.name + ', ' + start + ', ' + end + ')'
    

class slice_connection:
    def __init__(self, slice, connected_to):
        self.slice = slice
        self.connected_to = connected_to
    def __repr__(self):
        return "slice_connection(slice: " + str(self.slice) +' connected to: ' + str(self.connected_to) + ')'
    def __str__(self):
        return "slice_connection(slice: " + str(self.slice) +' connected to: ' + str(self.connected_to) + ')'


def are_variables_involved(nodes):
    if type(nodes) != list: nodes = [nodes]
    for i in range(0, len(nodes)):
        if nodes[i].kind == 'assignment': return True
        if nodes[i].kind == 'parameter': return True
        # Don't need to check if lower uses vars, if it is confirmed in upper
        if hasattr(nodes[i], 'parts'): 
            for part in nodes[i].parts:
                result = are_variables_involved(part)
                if result: return result
        if hasattr(nodes[i], 'list'):
            for part in nodes[i].list:
                result = are_variables_involved(part)
                if result: return result
        if hasattr(nodes[i], 'command'):  # some nodes are just pass through nodes
            result = are_variables_involved(part)
            if result: return result
        if hasattr(nodes[i], 'output'):   # some nodes are just pass through nodes
            result = are_variables_involved(part)
            if result: return result
    return False


def return_variable_commands(nodes):
    to_return = []
    for node in nodes:
        if are_variables_involved(node):
            to_return += [copy.deepcopy(node)]
    return to_return


def find_variable_slices(nodes):
    if type(nodes) is not list: nodes = [nodes]
    slices = {}
    for i, node in enumerate(nodes):
        assignments = bashparse.return_paths_to_node_type(node, 'assignment')
        evaluations = bashparse.return_variable_paths(node)

        for assignment in assignments:
            name = assignment.node.word.split('=')[0]
            if name not in slices: slices[name] = []
            slices[name] += [Slice(name, [i] + assignment.path, [i] + assignment.path)]
            # slices[name] += [Slice(name, [i], None)]

        for evaluation in evaluations:
            name = evaluation.node.value
            j = 0
            while name in slices and j < len(slices[name]):
                if slices[name][j].start > [i] + evaluation.path: break
                j += 1

            if j >= 0 and name in slices: 
                slices[name][j - 1].end = [i] + evaluation.path
            elif j < 0: raise ValueError('finding the slice went negative. idk how')
    return slices


def find_cd_slices(nodes):
    # This needs to be improved to take functions into account?
    if type(nodes) is not list: nodes = [nodes]
    slices = []
    # Retieve all the cd commands
    commands = bashparse.return_paths_to_node_type(nodes, 'command')
    cds = []
    for command in commands: 
        if hasattr(command.node.parts[0], 'word') and command.node.parts[0].word == 'cd': cds += [ command ]
    # Build the slices based off the cd commands found 
    i = 0
    while i < len(cds):
        slice_start = cds[i].path
        
        # If the cds are right next to one another then we are going to increment the slices cause chained cds should be in the same slice
        test = True
        while test and i + 1 < len(cds):

            if len(cds[i].path) == 1 and len(cds[i+1].path) == 1 and cds[i].path[0] + 1 == cds[i+1].path[0]: i += 1
            elif len(cds[i].path) == 2 and len(cds[i+1].path) == 2 and cds[i].path[0] + 1 == cds[i+1].path[0]: i += 1
                # Idk if this ^^ Is really good or necessary when its unrolled
            elif cds[i].path[-1] == cds[i+1].path[-1] + 1 and cds[i].path[:-1] == cds[i+1].path[:-1]: i += 1
            else: test = False
            
        # Set the value of the end of the slice
        if len(cds) > i + 1:  # If there is another cd between current location and EOF
            if cds[i+1].path[-1] > 0: slice_end =  cds[i+1].path[:-1] +  [ cds[i+1].path[-1] - 1 ]
            else: slice_end = cds[i+1].path[:-2] + [cds[i+1].path[-2] - 1] + [ 0 ]
        else:  # If there isn't a cd as the last line then set the final slice to the nodes from last cd to end of file
            slice_end = [ len(nodes) - 1 ]  # [ len(nodes) - 1, 0 ]  
        
        slices += [Slice('cd', slice_start, slice_end)]
        i += 1
    return slices
        
        
def is_connected(is_slice, connected_slice):
    if connected_slice.start[0] < is_slice.start[0] and connected_slice.end[0]: return True 
    if connected_slice.start[0] < is_slice.end[0] and connected_slice.end[0]: return True
    return False


def return_connected_slices(slices):
    variable_names = list(slices.keys())
    # Check every key we have in dict
    connected_slices = []
    for i, name in enumerate(variable_names):
        variable_slices = slices[name]
        # Check every slice we have associated with a given key
        for slice in variable_slices:
            # Check that slice vs all slices associated with every following key (meaning its a 100% compared)
            for j_name in variable_names[i+1:]:
                for j_slice in slices[j_name]:
                    if is_connected(slice, j_slice):
                        connected_slices += [slice_connection(slice, j_slice)]
    return connected_slices


def var_is_used_in_declaration(assignment_node, var_name):
    variables = bashparse.return_nodes_of_type(assignment_node, 'parameter')
    for var in variables: 
        if var.value == var_name: return True
    return False


def return_dependent_slices(connected_slices, orig_nodes):
    # 4 dependencies: nested in same slice, cd(?), used in the same line, used in definition, $2 acts on results of $1 command
    dependent_slices = []
    for slice in connected_slices:
        # Used in variable definition
        assignments = bashparse.return_paths_to_node_type(orig_nodes, 'assignment')
        for assignment in assignments:
            if assignment.path > slice.slice.start: # This might break with the introduction of cd as first entry
                is_dependent = False
                if assignment.node.word.split('=')[0] == slice.slice.name: is_dependent = var_is_used_in_declaration(assignment.node, slice.connected_to.name)
                if assignment.node.word.split('=')[0] == slice.connected_to.name: is_dependent = var_is_used_in_declaration(assignment.node, slice.slice.name)
                if is_dependent:
                    dependent_slices += [ slice ]
                    break
    
    return dependent_slices






# filename="testing.sh"

# nodes = bashparse.parse(open(filename).read())

# variable_assignments = bashparse.return_nodes_of_type(nodes, 'assignment')

# variable_uses = bashparse.return_variable_paths(nodes)

# variable_commands = return_variable_commands(nodes)

# slices = find_variable_slices(nodes)

# connected_slices = return_connected_slices(slices)

# dependent_slices = return_dependent_slices(connected_slices, nodes)

# print('dependent slices: ')
# for slice in dependent_slices:
#     print(slice)
