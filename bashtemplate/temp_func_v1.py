import bashtemplate.slice, bashtemplate.template, copy, bashparse




# Generalize nodes

def run_generalize_nodes(generalize_nodes):
    return basic_generalization(generalize_nodes)


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
