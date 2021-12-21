import bashparse, bashtemplate, bashunroll

filename="example.sh"

templates = bashtemplate.generate_templates_from_files(filename, {})

print('templates: ', templates)