from pyfiletree.ftree import FTree


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
