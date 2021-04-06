from pyfiletree.ftree import FTree, Node
import pdb


def test_ftree_read():
    def get_list_from_tree(node, l):
        l += [node.__str__()]
        for child in node.children:
            get_list_from_tree(child, l)
    ftree = FTree('E:\\PycharmProjects\\pyfiletree\\tests\\test.py', test=True)
    lst = []
    get_list_from_tree(ftree.root, lst)
    with open('E:\\PycharmProjects\\pyfiletree\\tests\\test.py', 'r') as f:
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
    file1 = FTree('E:\\PycharmProjects\\pyfiletree\\tests\\test.py')
    file2 = FTree('E:\\PycharmProjects\\pyfiletree\\tests\\test2.py')
    file3 = FTree('E:\\PycharmProjects\\pyfiletree\\tests\\test1_not_equal.py')

    assert file1 == file2
    assert file2 != file3

    file2.root.add_child(Node("error"))
    assert file1 != file2

    file1.root.add_child(Node("error"))
    assert file1 == file2
