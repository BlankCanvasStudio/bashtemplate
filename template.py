""" This file holds the definition of the template object """

class Template:

    def __init__(self, text = '', ratio = -1, raw_count = 1, weighted_count = None):
        self.text = text
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
    
