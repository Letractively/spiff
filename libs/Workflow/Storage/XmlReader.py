# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import os
import xml.dom.minidom as minidom
import Activities
from Exception  import StorageException
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

        self.logical_tags = {'equals':     Condition.EQUAL,
                             'not-equals': Condition.NOT_EQUAL}


    def _raise(self, error):
        raise StorageException('%s in XML file.' % error)


    def _read_logical(self, node):
        """
        Reads the logical tag from the given node, returns a Condition object.
        
        node -- the xml node (xml.dom.minidom.Node)
        """
        term1_attrib = node.getAttribute('left-field')
        term1_value  = node.getAttribute('left-value')
        op           = node.nodeName.lower()
        term2_attrib = node.getAttribute('right-field')
        term2_value  = node.getAttribute('right-value')
        kwargs       = {}
        if not self.logical_tags.has_key(op):
            self._raise('Invalid operator')
        if term1_attrib != '' and term1_value != '':
            self._raise('Both, left-field and left-value attributes found')
        elif term1_attrib == '' and term1_value == '':
            self._raise('left-field or left-value attribute required')
        elif term1_value != '':
            kwargs['left'] = term1_value
        else:
            kwargs['left_attribute'] = term1_attrib
        if term2_attrib != '' and term2_value != '':
            self._raise('Both, right-field and right-value attributes found')
        elif term2_attrib == '' and term2_value == '':
            self._raise('right-field or right-value attribute required')
        elif term2_value != '':
            kwargs['right'] = term2_value
        else:
            kwargs['right_attribute'] = term2_attrib
        return Condition(self.logical_tags[op], **kwargs)


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
                if activity_name is not None:
                    self._raise('Duplicate activity name %s' % activity_name)
                if node.firstChild is None:
                    self._raise('Successor tag without an activity name')
                activity_name = node.firstChild.nodeValue
            elif node.nodeName.lower() in self.logical_tags:
                if condition is not None:
                    self._raise('Multiple conditions are not yet supported')
                condition = self._read_logical(node)
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        if condition is None:
            self._raise('Missing condition in conditional statement')
        if activity_name is None:
            self._raise('A %s has no activity specified' % start_node.nodeName)
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
        type      = start_node.nodeName.lower()
        name      = start_node.getAttribute('name').lower()
        context   = start_node.getAttribute('context').lower()
        cancel    = start_node.getAttribute('cancel').lower()
        threshold = start_node.getAttribute('threshold').lower()
        kwargs    = {}
        if not self.activity_map.has_key(type):
            self._raise('Invalid activity type "%s"' % type)
        if type == 'startactivity':
            name = 'start'
        if name == '':
            self._raise('Invalid activity name "%s"' % name)
        if self.read_activities.has_key(name):
            self._raise('Duplicate activity name "%s"' % name)
        if cancel != '' and cancel != u'0':
            kwargs['cancel'] = True
        if threshold != '':
            kwargs['threshold'] = int(threshold)

        # Create a new instance of the activity.
        module = self.activity_map[type]
        if type == 'startactivity':
            activity = module(workflow)
        elif type == 'multiinstance':
            times_field = start_node.getAttribute('times-field').lower()
            times       = start_node.getAttribute('times').lower()
            if times == '' and times_field == '':
                self._raise('Missing "times" or "times-field" in "%s"' % name)
            elif times != '' and times_field != '':
                self._raise('Both, "times" and "times-field" in "%s"' % name)
            elif times != '':
                times    = int(times)
                activity = module(workflow, name, times = times)
            else:
                activity = module(workflow,
                                  name,
                                  times_attribute = times_field)
        elif context == '':
            activity = module(workflow, name, **kwargs)
        else:
            if not self.read_activities.has_key(context):
                self._raise('Context %s does not exist' % context)
            context  = self.read_activities[context][0]
            activity = module(workflow, name, context, **kwargs)

        # Walk through the children of the node.
        successors = []
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                pass
            elif node.nodeName == 'successor' \
              or node.nodeName == 'default-successor':
                if node.firstChild is None:
                    self._raise('Empty %s tag' % node.nodeName)
                successors.append((None, node.firstChild.nodeValue))
            elif node.nodeName == 'conditional-successor':
                successors.append(self._read_condition(workflow, node))
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        self.read_activities[name] = (activity, successors)


    def _read_workflow(self, start_node):
        """
        Reads the workflow from the given workflow node and returns a workflow
        object.
        
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        name = start_node.getAttribute('name')
        if name == '':
            self._raise('%s without a name attribute' % start_node.nodeName)

        # Read all activities and create a list of successors.
        workflow             = Workflow(name)
        self.read_activities = {'end': (StubActivity(workflow, 'End'), [])}
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                pass
            elif self.activity_map.has_key(node.nodeName.lower()):
                self.read_activity(workflow, node)
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        # Remove the default start-activity from the workflow.
        workflow.start = self.read_activities['start'][0]
        workflow.activities.pop(0)

        # Connect all activities.
        for name in self.read_activities:
            activity, successors = self.read_activities[name]
            for condition, successor_name in successors:
                if not self.read_activities.has_key(successor_name):
                    self._raise('Unknown successor: "%s"' % successor_name)
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