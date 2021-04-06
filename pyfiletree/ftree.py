from enum import Enum


class Level:
    UNASSIGNED = -2
    ROOT = -1


class Types(Enum):
    STATEMENT = 0
    FUNCTION = 1
    CLASS = 2
    EMPTY_LINE = 3


class Node:
    def __init__(self, value, level=Level.UNASSIGNED, debug=False, test=False):
        self.level = self.compute_level(value, level)
        self.value = value.lstrip()  # strip indentation
        self.children = []
        self.type = self.compute_type()
        self.DEBUG = debug
        self.TEST = test

    def __str__(self):
        if self.DEBUG:
            return f'{self.level * 4 * " "}{self.value[:-1]} --> {self.level} : {self.type.name}'
        if self.TEST:
            return f'{self.value}'
        return f'{self.level * 4 * " "}{self.value}'

    def __eq__(self, other):
        if isinstance(other, Node):
            # TODO: remove root comparison
            return Node.are_equal(self, other)
        return NotImplemented

    @staticmethod
    def are_equal(node1, node2):
        if (node1.value == node2.value or (node1.level == Level.ROOT and node2.level == Level.ROOT)) and \
                node1.level == node2.level:
            if len(node1.children) + len(node2.children) == 0:
                return True
            if len(node1.children) == len(node2.children):
                for child1, child2 in zip(node1.children, node2.children):
                    return Node.are_equal(child1, child2)
        return False

    def has_value(self, value_to_check):
        return self.value == value_to_check

    @staticmethod
    def compute_level(value, level):
        if level == Level.UNASSIGNED:  # level unassigned
            return (len(value) - len(value.lstrip())) // 4
        return level

    def compute_type(self):
        if self.value:
            if 'def' in self.value:
                return Types.FUNCTION
            if 'class' in self.value:
                return Types.CLASS
            return Types.STATEMENT
        return Types.EMPTY_LINE

    def add_child(self, child):
        self.children.append(child)

    def print_tree(self):
        end = '\n' if self.DEBUG or not self.value else ''
        print(self, end=end)
        for child in self.children:
            child.print_tree()


class FTree:
    def __init__(self, file_path, mode='r', debug=False, test=False):
        self.root = Node(file_path, Level.ROOT)
        self.mode = mode
        self.curr_line = 0
        self._stop_recursion = False
        self.DEBUG = debug
        self.TEST = test

        if 'r' in mode:
            self._build_reader_tree()

    def __eq__(self, other):
        if isinstance(other, FTree):
            return self.root == other.root
        return NotImplemented

    def _build_direct_children(self, father_node, lines):
        if self.curr_line < len(lines):
            curr_node = Node(lines[self.curr_line], debug=self.DEBUG, test=self.TEST)

            while curr_node.level >= father_node.level + 1:
                father_node.add_child(curr_node)
                prev_node = curr_node

                self.curr_line += 1
                if self.curr_line < len(lines):
                    curr_node = Node(lines[self.curr_line], debug=self.DEBUG, test=self.TEST)
                    if curr_node.has_value(''):
                        curr_node.level = father_node.level + 1
                else:
                    self._stop_recursion = True
                    break
                if curr_node.level > father_node.level + 1:
                    curr_node = self._build_direct_children(prev_node, lines)
                    if self._stop_recursion:
                        break

            if curr_node and curr_node.level < father_node.level + 1:
                return curr_node

    def _build_reader_tree(self):
        with open(self.root.value, 'r') as f:
            lines = f.readlines()
        self._build_direct_children(self.root, lines)
        self._stop_recursion = False
        self.curr_line = 0

    def print_tree(self):
        self.root.print_tree()

    def append(self, obj):
        if isinstance(obj, FTree):
            # TODO: append logic
            pass
        elif isinstance(obj, str):
            # TODO: read file + append
            # maybe then we can reverse these ifs
            pass
