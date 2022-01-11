import bashtemplate.slice, bashtemplate.template, copy, bashparse




# Generalize nodes

def run_generalize_nodes(generalize_nodes):
    # return basic_generalization(generalize_nodes)
    return parameter_tracking_generalization(generalize_nodes)
    #return variable_tracking_generalization(generalize_nodes)

def basic_generalization(generalize_nodes):
    # Basic replacement. 
    # Variables are not taken into account in this one
    # The use of local is not accounted for with this
    if type(generalize_nodes) is not list: generalize_nodes = [ generalize_nodes ]
    for node in generalize_nodes:
        if node.kind == 'word':
            node.word = '%d'
        if hasattr(node, 'parts'):
            if node.kind == 'command':
                if node.parts[0].kind == 'assignment':
                    node.parts[0].word = "%d=%d"
                for i in range(1, len(node.parts)):
                    node.parts[i].word = "%d"
            else:
                for part in node.parts:
                    basic_generalization(part)
                
        if hasattr(node, 'list'):
            for part in node.list:
                basic_generalization(part)
        if hasattr(node,'command'):
            basic_generalization(node.command)
        if hasattr(node, 'output'):
            basic_generalization(node.output)

            for i in range(1, len(node.parts)): node.parts[i].word = "%d"
    return generalize_nodes


def parameter_tracking_generalization(generalize_nodes):
    """ This replacement scheme tracks the parameters used to show any consistency 
    amoung the arguments. Start the parameter count at 0 and go up from there 
    referencing a dictionary to maintain internal consistency
    The number shouldn't matter but the pattern of the numbers will """
    if type(generalize_nodes) is not list: generalize_nodes = [ generalize_nodes ]
    params_used = {}
    param_num = 0
    for node in generalize_nodes:
        if node.kind == 'word':
            if node.word not in params_used: 
                params_used[node.word] = str(param_num) 
                param_num += 1
            node.word = '%' + params_used[node.word]
        if hasattr(node, 'parts'):
            if node.kind == 'command':
                if node.parts[0].kind == 'assignment':
                    # Should the variable assignments always be different? I think yes
                    # What about the values that are assigned?
                    value_assigned = node.parts[0].word.split('=', 1)[1]
                    if value_assigned not in params_used:
                        params_used[value_assigned] = param_num 
                        param_num += 1
                    node.parts[0].word = "%d=%" + str(params_used[value_assigned])
                for i in range(1, len(node.parts)):
                    if node.parts[i].word not in params_used: 
                        params_used[node.parts[i].word] = str(param_num) 
                        param_num += 1
                    node.parts[i].word = '%' + params_used[node.parts[i].word]
            else:
                for part in node.parts:
                    parameter_tracking_generalization(part)
                
        if hasattr(node, 'list'):
            for part in node.list:
                parameter_tracking_generalization(part)
        if hasattr(node,'command'):
            parameter_tracking_generalization(node.command)
        if hasattr(node, 'output'):
            parameter_tracking_generalization(node.output)

            for i in range(1, len(node.parts)): 
                if node.parts[i].word not in params_used: 
                    params_used[node.parts[i].word] = str(param_num) 
                    param_num += 1
                node.parts[i].word = '%' + params_used[node.parts[i].word]
    return generalize_nodes


def variable_tracking_generalization(generalize_nodes, params_used = {}, param_num = 0):
    """ This funciton tracks the variable usage through the 
    """
    print('in the function')
    if type(generalize_nodes) is not list: generalize_nodes = [ generalize_nodes ]
    for node in generalize_nodes:
        if node.kind == 'word':
            if node.word not in params_used: 
                params_used[node.word] = str(param_num) 
                param_num += 1
            node.word = '%' + params_used[node.word]
        if hasattr(node, 'parts'):
            if node.kind == 'command':
                if node.parts[0].kind == 'assignment':
                    # Theres no reason we can't use the param number here
                    # Should the variable assignments always be different? I think yes
                    # What about the values that are assigned?
                    variable_name, value_assigned = node.parts[0].word.split('=', 1)
                    # We should also assume its unrolled
                    if value_assigned not in params_used:
                        params_used[value_assigned] = str(param_num) 
                        param_num += 1
                    
                    params_used['$'+variable_name] = str(param_num) 
                    param_num += 1
                    
                    node.parts[0].word = "%" + params_used['$'+variable_name] +"=%" + params_used[value_assigned]
                for i in range(1, len(node.parts)):
                    node.parts = variable_tracking_generalization(node.parts[1:], params_used, param_num)

            else:
                for part in node.parts:
                    print('dict: ', params_used)
                    if part.kind != 'parameter':
                        parameter_tracking_generalization(part)
                    elif '$'+part.value in params_used:
                        print('here2')
                        node.word = node.word.replace(part.value, '%'+params_used['$'+part.value])
                        node.parts.remove(part)

        if hasattr(node, 'list'):
            for part in node.list:
                parameter_tracking_generalization(part)
        if hasattr(node,'command'):
            parameter_tracking_generalization(node.command)
        if hasattr(node, 'output'):
            parameter_tracking_generalization(node.output)

            for i in range(1, len(node.parts)): 
                if node.parts[i].word not in params_used: 
                    params_used[node.parts[i].word] = str(param_num) 
                    param_num += 1
                node.parts[i].word = '%' + params_used[node.parts[i].word]
    return generalize_nodes



# identify template slices

def run_identify_slices(nodes):
    return identify_variable_slices(nodes)


def identify_variable_slices(nodes):
    # This is just going to grab slice indexes based on the variable locations
    slices = []
    assignment_slices = bashtemplate.slice.find_variable_slices(nodes)
    for key in assignment_slices.keys():
        # Strip out just the slices. Don't care about the variables involved
        slices += assignment_slices[key]
    # connected_slices = return_connected_slices(assignment_slices)
    # dependent_slices = return_dependent_slices(connected_slices, nodes)
    # slices += assignment_slices
    cd_slices = bashtemplate.slice.find_cd_slices(nodes)
    slices += cd_slices
    
    return slices




# generate the templaces from slices

def run_generate_templates(slices, nodes):
    # primative turn every slice into a template
    templates = []
    for slce in slices:
        text = ''
        for i in range(slce.start[0], slce.end[0] + 1):
            text += bashparse.convert_tree_to_string(nodes[i]) + ' ; '
        text = text[:-1]
        new_template = bashtemplate.Template(text = text, slices = [ slce ], ratio = ( ( slce.end[0] - slce.start[0] + 1 ) / len(nodes) ), raw_count = 1)
        if new_template not in templates: templates += [ copy.deepcopy(new_template) ]
        else: templates[templates.index(new_template)].inc_counts()
    return templates




# find the usefule templates

def run_find_useful_templates(template_record):
    # basic filtering alg: don't
    templates = []
    for key in template_record.keys():
        templates += [ template_record[key] ]
    
    return templates




# Update the nodes (ie unroll and replace them)

def run_update_nodes(nodes):
    var_list = bashparse.update_variable_list_with_node(nodes, {})
    nodes = bashparse.substitute_variables(nodes, var_list)
    return nodes
