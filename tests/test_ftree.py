from pyfiletree.ftree import FTree, Node


def test_ftree_read():
    def get_list_from_tree(node, l):
        l += [node.__str__()]
        for child in node.children:
            get_list_from_tree(child, l)
    ftree = FTree('tests\\test.py', test=True)
    lst = []
    get_list_from_tree(ftree.root, lst)
    with open('tests\\test.py', 'r') as f:
        actual_list = [line.lstrip() for line in f.readlines()]
    assert lst[1:] == actual_list


def test_node_eq():
    assert Node("value") == Node("value")
    parent1 = Node("parent")
    parent1.add_child(Node('child', level=2))

    parent2 = Node("parent")
    parent2.add_child(Node('child', level=2))

    assert parent1 == parent2

    parent2 = Node("parent2")
    parent2.add_child(Node('child', level=2))

    assert parent2 != parent1

    parent2 = Node("parent")
    parent2.add_child(Node('child2', level=2))

    assert parent2 != parent1

    parent2 = Node("parent")
    parent2.add_child(Node('child', level=3))

    assert parent1 != parent2


def test_ftree_eq():
    file1 = FTree('tests\\test.py')
    file2 = FTree('tests\\test2.py')
    file3 = FTree('tests\\test1_not_equal.py')

    assert file1 == file2
    assert file2 != file3

    file2.root.add_child(Node("error"))
    assert file1 != file2

    file1.root.add_child(Node("error"))
    assert file1 == file2


def test_ftree_write():
    file1 = FTree('tests\\test.py')
    file1.root.add_child(Node("error"))
    file1.write_to('tests\\test3.py', mode='w+')
    file2 = FTree('tests\\test3.py')
    assert file1 == file2


def test_node_line_value():
    file1 = FTree('tests\\test.py')
    assert file1.root.line == 0
    assert file1.root.children[0].line == 1
    assert file1.root.children[3].children[1].children[1].line == 8


def test_node_update_line():
    file1 = FTree('tests\\test.py')

    prev_line_value = file1.root.children[3].line
    assert file1.root.children[3].children[1].children[1].line == 8
    file1.root.children[3].update_line(3)
    assert file1.root.children[3].line == prev_line_value + 3
    assert file1.root.children[3].children[1].children[1].line == 11


def test_ftree_father_nodes():
    file1 = FTree('tests\\test.py')
    assert file1.root.father is None

    child_of_root = file1.root.children[-1]
    assert child_of_root.father == file1.root

    father_of_other = file1.root.children[3]
    child_of_other = father_of_other.children[-1]
    assert child_of_other.father == father_of_other


# noinspection PyBroadException
def test_get_node_by_line():
    file1 = FTree('tests\\test.py')
    assert file1.root.line == 0
    assert file1.root == file1.get_node_by_line(0)

    try:
        _ = file1.get_node_by_line(1230)
    except Exception:
        assert 1 == 1
    else:
        assert 1 != 1

    def_node = file1.root.children[3]
    if_x_node = def_node.children[1]
    assert file1.get_node_by_line(1) == file1.root.children[0]
    assert file1.get_node_by_line(4) == def_node
    assert file1.get_node_by_line(6) == if_x_node
    assert file1.get_node_by_line(9) == if_x_node.children[1].children[0]


def test_ftree_append():
    file1 = FTree('tests\\test.py')
    file_to_append = FTree('tests\\file_to_append.py')
    
    assert file1.root.children[0].line == 1
    
    file1.append('tests\\file_to_append.py')
    assert file1.root.children[-1] == file_to_append.root.children[-1]
    
    file1.append('tests\\file_to_append.py', line=1)
    file1.write_to('tests\\test3.py')
    assert file1.root.children[2].line == 3
    assert file1.root.children[5].children[1].children[1].line == 9
