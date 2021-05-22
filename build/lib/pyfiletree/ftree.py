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
    def __init__(self, value, father_node=None, line=-1, level=Level.UNASSIGNED, debug=False, test=False):
        self.level = self.compute_level(value, level)
        self.value = value.lstrip()  # strip indentation
        self.line = line + 1
        self.children = []
        self.father = father_node
        self.type = self.compute_type()
        self.DEBUG = debug
        self.TEST = test
        self._stop_recursion = False

    def __str__(self):
        if self.DEBUG:
            return f'{self.level * 4 * " "}{self.value[:-1]} --> {self.level} : {self.father.value}'
        if self.TEST:
            return f'{self.value}'
        return f'{self.level * 4 * " "}{self.value}'

    def __eq__(self, other):
        if isinstance(other, Node):
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

    def add_child(self, node):
        self.children.append(node)

    def add_children(self, children, node_to_be_replaced=None, line=-1, debug=False):
        if line == -1:
            line_offset = self.children[-1].line + 1
            for child in children:
                child.update_line(line_offset)
                child.father = self
                child.DEBUG = debug
            self.children.extend(children)
        else:
            idx_to_be_replaced = self.children.index(node_to_be_replaced)

            # update lines and lvls in children to be appended
            for child in children:
                child.update_line(line + children.index(child) - 1, 0)
                child.update_level(self.level)
                child.father = self
                child.DEBUG = debug

            self.children[idx_to_be_replaced:idx_to_be_replaced] = children

    def print_tree(self):
        end = '\n' if self.DEBUG or not self.value else ''
        print(self, end=end)
        for child in self.children:
            child.print_tree()

    def get_node_list(self, lst):
        if self.level != Level.ROOT:
            lst.append(self)
        for child in self.children:
            child.get_node_list(lst)

    def update_line(self, offset, new_line=None):
        self.line = new_line or self.line
        self.line += offset
        for child in self.children:
            child.update_line(offset)

    def update_level(self, fathers_lvl):
        self.level = fathers_lvl + 1
        for child in self.children:
            child.update_level(self.level)

    def update_lines_globally(self, line_tresh, offset):
        if self.line >= line_tresh:
            self.line += offset
        for child in self.children:
            child.update_lines_globally(line_tresh, offset)

    @staticmethod
    def get_real_length(children):
        offset = len(children)
        for child in children:
            offset += Node.get_real_length(child.children)
        return offset


class FTree:
    def __init__(self, file_path, transformer=None, debug=False, test=False):
        self.root = Node(file_path, father_node=None, level=Level.ROOT)
        self.list_nodes = []
        self.curr_line = 0
        self._stop_recursion = False
        self.transformer = transformer  # TODO: define a setter for this; make it protected
        self.DEBUG = debug
        self.TEST = test

        self._build_reader_tree()

    def __eq__(self, other):
        if isinstance(other, FTree):
            other._get_node_list()
            self._get_node_list()
            len_other = len(other.list_nodes)
            len_self = len(self.list_nodes)
            return len_self == len_other and self.root == other.root
        return NotImplemented

    def _build_direct_children(self, father_node, lines):
        if self.curr_line < len(lines):
            curr_node = Node(lines[self.curr_line],
                             father_node=father_node,
                             line=self.curr_line,
                             debug=self.DEBUG,
                             test=self.TEST)

            while curr_node.level >= father_node.level + 1:
                father_node.add_child(curr_node)
                prev_node = curr_node

                self.curr_line += 1
                if self.curr_line < len(lines):
                    curr_node = Node(lines[self.curr_line],
                                     father_node=father_node,
                                     line=self.curr_line,
                                     debug=self.DEBUG,
                                     test=self.TEST)
                    if curr_node.has_value(''):
                        curr_node.level = father_node.level + 1
                else:
                    self._stop_recursion = True
                    break
                if curr_node.level > father_node.level + 1:
                    curr_node = self._build_direct_children(prev_node, lines)
                    if curr_node:
                        curr_node.father = father_node
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

    def _get_node_list(self):
        self.list_nodes = []
        self.root.get_node_list(self.list_nodes)

    def _update_lines_globally(self, line_tresh, offset):
        self.root.update_lines_globally(line_tresh, offset)

    def _get_node_by_line(self, node, line):
        if not self._stop_recursion:
            if node.line == line:
                self._stop_recursion = True
                return node
            for child in node.children:
                found_node = self._get_node_by_line(child, line)
                if self._stop_recursion:
                    return found_node

    def get_node_by_line(self, line):
        self._stop_recursion = False
        node = self._get_node_by_line(self.root, line)
        if not node:
            raise Exception(f'No node at line {line}')
        return node

    def append(self, obj, line=-1):
        # TODO append node
        if isinstance(obj, FTree):
            children_to_append = obj.root.children
            if line == -1:  # append to the end of tree: move children from root to root and update lines
                self.root.add_children(children_to_append, debug=self.DEBUG)
            else:
                curr_node = self.get_node_by_line(line)
                offset = Node.get_real_length(children_to_append)
                self._update_lines_globally(line, offset)
                curr_node.father.add_children(children_to_append, curr_node, line, debug=self.DEBUG)
        elif isinstance(obj, str):
            ftree = FTree(obj)
            self.append(ftree, line=line)

    def write_to(self, path, mode='a+'):
        self._get_node_list()
        with open(path, mode=mode) as f:
            for node in self.list_nodes:
                if node.value == '':
                    node.value = '\n'
                f.write(node.__str__())

    def print_tree(self):
        self.root.print_tree()

    def apply_transformer(self):
        # TODO: specify lines/threshold line for which to apply this list of funcs
        self._get_node_list()
        if self.transformer:
            for node in self.list_nodes:
                for func in self.transformer:
                    node.value = func(node.value)
        else:
            raise Exception("Transformer empty")
