""" This file holds the definition of the template object """

class Template:

    def __init__(self, text = '', slices = [None], ratio = -1, raw_count = 1):
        if type(slices) is not list: slices = [slices]
        self.text = text
        self.slices = slices
        self.ratio = ratio
            # The length of the template relative to the file 
            # This can be used to control the granulatiry of the templating system
        self.raw_count = raw_count  # raw number of times template has appeared
        self.weighted_count = (self.raw_count * self.ratio)  
            # Number of times a template has appeared weighted by the length of the template
            # We can use this to favor longer templates unless is occurs ALL the time
    
    def inc_counts(self, inc_num = 1):
        self.raw_count += inc_num
        self.weighted_count += (inc_num * self.ratio)
    
    def __str__(self):
        return 'Template("' + self.text + '", ratio: ' + str(self.ratio) + ', raw count: ' + str(self.raw_count) + ', weighted count: ' + str(self.raw_count * self.ratio) + ')'
    
    def __repr__(self):
        return 'Template("' + self.text + '", ratio: ' + str(self.ratio) + ', raw count: ' + str(self.raw_count) + ', weighted count: ' + str(self.raw_count * self.ratio) + ')'

    def __eq__(self, obj):
        return self.text == obj.text
    
