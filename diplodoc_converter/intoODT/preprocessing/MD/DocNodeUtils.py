class DocNodeUtils:
    @staticmethod
    def getDocNode_parent_dir(current_node):
        current_node_path_parent = DocNodeUtils.getDocNode_parent(current_node)
        return current_node_path_parent.resolve()

    @staticmethod
    def getDocNode_parent(current_node):
        current_node_path = current_node.path
        return current_node_path.parent
