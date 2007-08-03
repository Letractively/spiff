import os
import xml.dom.minidom as minidom
import Activities
from Workflow   import Workflow
from Activities import *

class XmlReader(object):
    """
    Parses XML into a workflow object.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.read_activities = {}

        # Create a list of all activities.
        self.activity_map = {}
        for name in dir(Activities):
            if name.startswith('_'):
                continue
            module = Activities.__dict__[name]
            self.activity_map[name.lower()] = module

        self.logical_tags = {'equals':     Activities.MultiChoice.EQUAL,
                             'not-equals': Activities.MultiChoice.NOT_EQUAL}


    def _read_logical(self, node):
        """
        Reads the logical tag from the given node, returns a tuple
        (term1, op, term2).
        
        node -- the xml node (xml.dom.minidom.Node)
        """
        term1 = node.getAttribute('field-value')
        op    = node.nodeName.lower()
        term2 = node.getAttribute('other-value')
        assert op in self.logical_tags.keys()
        return (term1, self.logical_tags[op], term2)


    def _read_condition(self, workflow, start_node):
        """
        Reads the conditional statement from the given node.
        
        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Collect all information.
        condition     = None
        activity_name = None
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() == 'successor':
                assert activity_name   is None # Duplicates not allowed.
                assert node.firstChild is not None
                activity_name = node.firstChild.nodeValue
            elif node.nodeName.lower() in self.logical_tags:
                assert condition is None # Duplicates not yet supported.
                condition = self._read_logical(node)
            else:
                raise Exception("Unknown node: %s" % node.nodeName)

        if activity_name is None:
            raise Exception("%s has no successor" % start_node.nodeName)
        return (condition, activity_name)


    def read_activity(self, workflow, start_node):
        """
        Reads the activity from the given node and returns a tuple
        (start, end) that contains the stream of objects that model
        the behavior.
        
        workflow -- the workflow with which the activity is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Extract attributes from the node.
        type    = start_node.nodeName.lower()
        name    = start_node.getAttribute('name').lower()
        context = start_node.getAttribute('context').lower()
        assert self.activity_map.has_key(type)
        if type == 'startactivity':
            name = 'start'
        if name == '':
            raise Exception("Invalid activity name: '%s'" % name)
        if self.read_activities.has_key(name):
            raise Exception("Duplicate activity name %s" % name)

        # Create a new instance of the activity.
        module = self.activity_map[type]
        if type == 'startactivity':
            activity = module(workflow)
        elif context == '':
            activity = module(workflow, name)
        else:
            if not self.read_activities.has_key(context):
                raise Exception("Context %s does not exist" % context)
            context  = self.read_activities[context][0]
            activity = module(workflow, name, context)

        # Walk through the children of the node.
        successors = []
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                pass
            elif node.nodeName == 'successor' \
              or node.nodeName == 'default-successor':
                assert node.firstChild is not None
                successors.append((None, node.firstChild.nodeValue))
            elif node.nodeName == 'conditional-successor':
                successors.append(self._read_condition(workflow, node))
            else:
                raise Exception("Unknown node: %s" % node.nodeName)

        self.read_activities[name] = (activity, successors)


    def _read_workflow(self, start_node):
        """
        Reads the workflow from the given workflow node and returns a workflow
        object.
        
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        name = start_node.getAttribute('name')
        assert name is not None

        # Read all activities and create a list of successors.
        workflow             = Workflow(name)
        self.read_activities = {'end': (workflow.end, [])}
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                pass
            elif self.activity_map.has_key(node.nodeName.lower()):
                self.read_activity(workflow, node)
            else:
                raise Exception("Unknown node: %s" % node.nodeName)

        # Remove the default start-activity from the workflow.
        workflow.start = self.read_activities['start'][0]
        workflow.activities.pop(0)

        # Connect all activities.
        for name in self.read_activities:
            activity, successors = self.read_activities[name]
            for condition, successor_name in successors:
                if not self.read_activities.has_key(successor_name):
                    raise Exception("Unknown successor: %s" % successor_name)
                successor, foo = self.read_activities[successor_name]
                if condition is None:
                    activity.connect(successor)
                else:
                    activity.connect_if(condition, successor)
        return workflow


    def read(self, xml):
        """
        Reads all workflows from the given XML structure and returns a
        list of workflow object.
        
        xml -- the xml structure (xml.dom.minidom.Node)
        """
        workflows = []
        for node in xml.getElementsByTagName('process-definition'):
            workflows.append(self._read_workflow(node))
        return workflows


    def parse_string(self, string):
        """
        Reads the workflow XML from the given string and returns a workflow
        object.
        
        string -- the name of the file (string)
        """
        return self.read(minidom.parseString(string))


    def parse_file(self, filename):
        """
        Reads the workflow XML from the given file and returns a workflow
        object.
        
        filename -- the name of the file (string)
        """
        return self.read(minidom.parse(filename))
