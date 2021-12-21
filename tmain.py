import bashparse, bashunroll, copy


"""
    Logical structure:  ( loop until done ){ generate_templates -> filter_templates -> add_templates } -> find_useful_templates -> QED
"""


def generalize_nodes(nodes):
    """ This function takes nodes and returns their most general form 
    (ie without using specific parameters). This will return a list of nodes """
    
    if type(nodes) is not list: nodes = [nodes]
    generalized_nodes = copy.deepcopy(nodes)

    return generalized_nodes


def generate_templates(nodes):
    """ This function takes an array of nodes and returns the templates generated """
    
    if type(nodes) is not list: nodes = [nodes]
    nodes = generalize_nodes(nodes)
    templates = []

    return templates


def filter_templates(templates):
    """ This takes an array of templates and returns on the necessary templates from 
    the complete list of templates generated. This is separated from generate_templates 
    for modularity and to allow filtering to be a different concept from the generation """

    filtered_templates = copy.deepcopy(templates)

    return filtered_templates


def add_templates(templates, template_record):
    """ This function takes in the templates & current template records and returns the updated 
    template_record object. It adds all templates to the template_record object. The record object 
    is going to be used to idetify any important templates / trends. """
    
    
    return template_record


def find_useful_templates(template_record):
    """ This function takes the template_record and returns an array of any templates deemed to be useful """
    useful_templates = []
    
    return useful_templates


def generate_nodes_from_file(filename):
    """ Takes a file name and then returns all the nodes, in order, in that file as an array """
    """ The unrolling should be done here """
    
    file_text = open(filename).read()
    nodes = bashparse.parse(file_text)
    unrolled_nodes = bashunroll.replacement_based_unroll(nodes, var_list = {})
    return unrolled_nodes


def generate_template_record_from_files(filenames, template_record):
    """ This function takes a filename or a list of filenames, reads the files, updates the template_record
    object with all of the templates found in the files. Returns the template_record object """
    
    if type(filenames) is not list: filenames = [filenames]
    for filename in filenames: 
        nodes = generate_nodes_from_file(filename)
        templates = generate_templates(nodes)
        filtered_templates = filter_templates(templates)
        template_record = add_templates(filtered_templates, template_record)
    return template_record


def generate_templates_from_files(filenames, template_record):
    """ This function takes the list of filenames and generates the templates found in those files.
    This function returns an array of all the templates found in the file(s) """
    
    template_record = generate_template_record_from_files(filenames, template_record)
    important_templates = find_useful_templates(template_record)
    return important_templates